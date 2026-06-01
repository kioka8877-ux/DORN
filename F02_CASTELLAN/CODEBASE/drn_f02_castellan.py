"""
drn_f02_castellan.py — Frégate F02 CASTELLAN
==============================================
PENTERACT DORN V3 — VIIe Légion

HUD de contrôle et simulation. L'opérateur visualise l'animation avec
prévisualisation caméra active, corrige le plan_de_vol.json en temps réel,
puis fige le plan de vol fusionné pour F03.
Stack : Streamlit + Canvas JS + math.js (CDN).

Usage (Colab — depuis DRN_F02.ipynb) :
    streamlit run drn_f02_castellan.py -- --drive-base /content/drive/MyDrive/DRIVE_DORN

Entrées  : F02_CASTELLAN/IN/plan_de_vol.json   (sans camera_plan, sorti de F01)
           F02_CASTELLAN/IN/camera_plan.json    (sorti de META_CAMERA — fichier séparé)
           F02_CASTELLAN/IN/images/*.png
Sorties  : F02_CASTELLAN/OUT/plan_de_vol.json  (fusionné, validated_by_magos: true)
"""

import argparse
import copy
import datetime
import json
import os
import sys

import streamlit as st
import streamlit.components.v1 as components

# ─── Configuration ─────────────────────────────────────────────────────────────

DEFAULT_DRIVE_BASE = "/content/drive/MyDrive/DRIVE_DORN"

REVEAL_STYLES    = ["linear", "ease_in", "ease_out", "ease_in_out", "dramatic"]
MOVEMENT_ENERGY  = ["calm", "cinematic", "aggressive", "viral_edit"]
GEOMETRY_MODES   = ["cartesian", "polar"]
FORMATS          = ["vertical", "horizontal"]

# ─── Args (Streamlit passe les args après '--') ────────────────────────────────

def get_drive_base():
    try:
        idx = sys.argv.index("--")
        args = sys.argv[idx + 1:]
    except ValueError:
        args = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--drive-base", default=DEFAULT_DRIVE_BASE)
    return parser.parse_args(args).drive_base

# ─── JSON helpers ──────────────────────────────────────────────────────────────

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ─── Canvas HTML ───────────────────────────────────────────────────────────────

def build_canvas_html(data):
    fmt = data.get("concept_metadata", {}).get("format", "vertical")
    cw, ch = (360, 460) if fmt == "vertical" else (560, 300)
    cfg = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    json_str = cfg.replace("'", "\\'")

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjs/11.11.0/math.min.js"></script>
<style>
body{{background:#0a0a0f;color:#ccc;font-family:monospace;margin:0;padding:6px}}
canvas{{display:block;margin:0 auto;background:#0a0a0f}}
#slider{{width:100%;margin:6px 0;accent-color:#00FFD1}}
#info{{text-align:center;font-size:11px;color:#777;margin-bottom:3px}}
#ttl{{text-align:center;font-size:12px;color:#eee;margin-bottom:5px;font-weight:bold}}
#camBtn{{display:block;margin:4px auto;padding:4px 20px;background:#1a1a2e;border:1px solid #00FFD1;color:#00FFD1;cursor:pointer;font-family:monospace;font-size:11px;letter-spacing:1px}}
#camBtn.on{{background:#00FFD1;color:#0a0a0f;font-weight:bold}}
#snapBtn{{display:block;margin:8px auto;padding:3px 14px;background:#1a1a2e;border:1px solid #333;color:#555;cursor:pointer;font-family:monospace;font-size:10px}}
.snaps{{display:flex;gap:4px;justify-content:center;margin-top:6px}}
.snap-item{{flex:1;text-align:center}}
.snap-item canvas{{width:100%;height:auto;border:1px solid #1a1a2e;display:block}}
.snap-label{{font-size:9px;color:#444;margin-top:2px}}
#segBar{{font-size:9px;color:#333;text-align:center;margin:3px 0;line-height:1.8}}
</style></head><body>
<div id="ttl"></div>
<canvas id="sim" width="{cw}" height="{ch}"></canvas>
<input type="range" id="slider" min="0" max="1000" value="500">
<div id="info">x=0 | t=0.00s | frame 0</div>
<button id="camBtn" onclick="toggleCam()">CAMERA : OFF</button>
<div id="segBar"></div>
<button id="snapBtn" onclick="generateSnapshots()">[ GÉNÉRER SNAPSHOTS CAMÉRA ]</button>
<div class="snaps">
  <div class="snap-item"><canvas id="s0" width="{cw}" height="{ch}"></canvas><div class="snap-label" id="l0">—</div></div>
  <div class="snap-item"><canvas id="s1" width="{cw}" height="{ch}"></canvas><div class="snap-label" id="l1">—</div></div>
  <div class="snap-item"><canvas id="s2" width="{cw}" height="{ch}"></canvas><div class="snap-label" id="l2">—</div></div>
</div>
<script>
const C=JSON.parse('{json_str}');
const cam=C.camera_plan||null;
const cnv=document.getElementById('sim'),ctx=cnv.getContext('2d');
const sld=document.getElementById('slider'),inf=document.getElementById('info');
document.getElementById('ttl').textContent=C.concept_metadata?.title||'';
const W=cnv.width,H=cnv.height,PL=50,PR=20,PT=30,PB=40;
const PW=W-PL-PR,PHT=H-PT-PB;
const t=C.timing||{{}},xS=t.x_range?.start??0,xE=t.x_range?.end??10;
const fps=t.fps??60,spf=t.step_per_frame??0.05;
const cc=t.complexity_coefficient??1.0,frz=t.final_freeze_frames??180;
const revF=Math.round((xE-xS)/spf),totF=Math.round(revF*cc)+frz;
const geo=C.space_environment?.geometry_mode??'cartesian';
let cameraMode=false;

// ─── Camera ──────────────────────────────────────────────────────────────────

function getActiveSeg(frame){{
  if(!cam)return null;
  const segs=cam.camera_segments||[];
  for(let s of segs){{if(frame>=s.start_frame&&frame<=s.end_frame)return s;}}
  return segs.length?segs[segs.length-1]:null;
}}

function toggleCam(){{
  cameraMode=!cameraMode;
  const btn=document.getElementById('camBtn');
  btn.textContent='CAMERA : '+(cameraMode?'ON':'OFF');
  btn.className=cameraMode?'on':'';
  if(!cam){{inf.textContent='WARN: aucun camera_plan dans le JSON.';return;}}
  draw(sld.value/1000);
}}

(function buildSegBar(){{
  if(!cam){{document.getElementById('segBar').textContent='— camera_plan absent —';return;}}
  const segs=cam.camera_segments||[];
  document.getElementById('segBar').innerHTML=
    '<span style="color:#222">CAM SEGS: </span>'+
    segs.map(s=>`<span style="color:#444">[${{s.start_frame}}–${{s.end_frame}} | ${{s.mode}} | z${{s.zoom}}]</span>`).join(' ');
}})();

// ─── Math helpers ────────────────────────────────────────────────────────────

function evalCurve(expr,xv){{
  try{{let y=math.evaluate(expr,{{x:xv,theta:xv}});
    if(y&&typeof y==='object'&&'re'in y)y=y.re;
    return isFinite(y)?y:null;}}catch{{return null;}}
}}

function sampleCart(expr,xCur,n=250){{
  const pts=[],dx=(xCur-xS)/n;
  if(dx<=0)return pts;
  for(let i=0;i<=n;i++){{const xv=xS+i*dx,y=evalCurve(expr,xv);if(y!==null)pts.push([xv,y]);}}
  return pts;
}}

function samplePolar(expr,tCur,n=350){{
  const pts=[],dth=(tCur-xS)/n;
  if(dth<=0)return pts;
  for(let i=0;i<=n;i++){{const th=xS+i*dth;
    try{{let r=math.evaluate(expr,{{theta:th,x:th}});
      if(r&&typeof r==='object'&&'re'in r)r=r.re;
      if(isFinite(r))pts.push([r,th]);}}catch{{}}}}
  return pts;
}}

function yRange(curves,xCur){{
  let mn=Infinity,mx=-Infinity;
  curves.forEach(c=>{{sampleCart(c.math_input,xCur).forEach(([_,y])=>{{mn=Math.min(mn,y);mx=Math.max(mx,y);}});}});
  if(!isFinite(mn)){{mn=-1;mx=1;}}
  const p=(mx-mn)*0.12||0.5;return[mn-p,mx+p];
}}

function toXY(xv,yv,mn,mx){{
  return[PL+((xv-xS)/(xE-xS))*PW, PT+(1-(yv-mn)/(mx-mn))*PHT];
}}

function toPolar(r,th,rMax){{
  const sc=Math.min(PW,PHT)/2;
  return[W/2+(r/rMax)*sc*Math.cos(th),H/2-(r/rMax)*sc*Math.sin(th)];
}}

// ─── Draw helpers ────────────────────────────────────────────────────────────

function drawGrid(mn,mx){{
  ctx.strokeStyle='#151525';ctx.lineWidth=1;
  for(let i=0;i<=5;i++){{const x=PL+(i/5)*PW;ctx.beginPath();ctx.moveTo(x,PT);ctx.lineTo(x,PT+PHT);ctx.stroke();}}
  for(let i=0;i<=4;i++){{const y=PT+(i/4)*PHT;ctx.beginPath();ctx.moveTo(PL,y);ctx.lineTo(PL+PW,y);ctx.stroke();}}
  ctx.fillStyle='#444';ctx.font='9px monospace';ctx.textAlign='center';
  for(let i=0;i<=5;i++)ctx.fillText((xS+(i/5)*(xE-xS)).toFixed(1),PL+(i/5)*PW,PT+PHT+14);
  ctx.textAlign='right';
  for(let i=0;i<=4;i++)ctx.fillText((mx-(i/4)*(mx-mn)).toFixed(1),PL-4,PT+(i/4)*PHT+4);
  ctx.fillStyle='#666';ctx.font='10px monospace';ctx.textAlign='center';
  ctx.fillText(C.space_environment?.x_label||'x',W/2,H-2);
  ctx.save();ctx.translate(11,H/2);ctx.rotate(-Math.PI/2);
  ctx.fillText(C.space_environment?.y_label||'y',0,0);ctx.restore();
}}

function drawCartCurve(c,xCur,mn,mx){{
  const pts=sampleCart(c.math_input,xCur);if(pts.length<2)return null;
  const col=c.render_style?.color_hex||'#00FFD1';
  const glo=c.render_style?.glow_radius_px||20;
  const lw=c.render_style?.line_width_px||6;
  ctx.save();ctx.shadowBlur=glo;ctx.shadowColor=col;
  ctx.strokeStyle=col;ctx.lineWidth=lw;ctx.lineJoin='round';ctx.lineCap='round';
  ctx.beginPath();
  pts.forEach(([xv,yv],i)=>{{const[px,py]=toXY(xv,yv,mn,mx);i===0?ctx.moveTo(px,py):ctx.lineTo(px,py);}});
  ctx.stroke();ctx.restore();
  const[lx,ly]=toXY(pts[pts.length-1][0],pts[pts.length-1][1],mn,mx);
  ctx.save();ctx.shadowBlur=glo*1.5;ctx.shadowColor=col;ctx.fillStyle='#fff';
  ctx.beginPath();ctx.arc(lx,ly,5,0,Math.PI*2);ctx.fill();ctx.restore();
  return[lx,ly];
}}

function drawPolarCurve(c,tCur){{
  const pts=samplePolar(c.math_input,tCur);if(pts.length<2)return;
  const rMax=Math.max(...pts.map(([r])=>Math.abs(r)))||1;
  const col=c.render_style?.color_hex||'#00FFD1';
  const glo=c.render_style?.glow_radius_px||20;
  const lw=c.render_style?.line_width_px||6;
  ctx.save();ctx.shadowBlur=glo;ctx.shadowColor=col;
  ctx.strokeStyle=col;ctx.lineWidth=lw;ctx.lineJoin='round';
  ctx.beginPath();
  pts.forEach(([r,th],i)=>{{const[px,py]=toPolar(r,th,rMax);i===0?ctx.moveTo(px,py):ctx.lineTo(px,py);}});
  ctx.stroke();ctx.restore();
}}

function drawFreezeOverlay(){{
  const ann=C.final_frame?.annotation||'';
  ctx.save();
  ctx.fillStyle='rgba(0,0,0,0.55)';ctx.fillRect(PL,PT+PHT*0.6,PW,PHT*0.32);
  ctx.fillStyle='#FFD700';ctx.font='bold 12px monospace';ctx.textAlign='center';
  ctx.fillText(ann,W/2,PT+PHT*0.78);
  ctx.fillStyle='#00FFD1';ctx.font='10px monospace';
  ctx.fillText('[ FREEZE — FINAL FRAME ]',W/2,PT+PHT*0.88);
  ctx.restore();
}}

// ─── Camera transform ────────────────────────────────────────────────────────

function applyCamTransform(frame,mn,mx){{
  const seg=getActiveSeg(frame);
  if(!seg)return false;
  const zoom=seg.zoom||1.0;
  const shk=seg.shake||0;
  const shakeX=Math.sin(frame*7.31+1.2)*shk*8;
  const shakeY=Math.cos(frame*5.73+0.7)*shk*8;
  let panX=(seg.x_offset||0)+shakeX;
  let panY=(seg.y_offset||0)+shakeY;
  // follow_asset: pan to keep target curve endpoint at canvas center
  if(seg.mode==='follow_asset'&&seg.target_curve_id&&mn!==undefined){{
    const tc=(C.reactor_curves||[]).find(c=>c.id===seg.target_curve_id);
    if(tc){{
      const revP=Math.min(frame/revF,1.0);
      const xCur=xS+(xE-xS)*revP;
      const pts=sampleCart(tc.math_input,xCur,20);
      if(pts.length>0){{
        const[lxv,lyv]=pts[pts.length-1];
        const[lpx,lpy]=toXY(lxv,lyv,mn,mx);
        panX+=zoom*(W/2-lpx);
        panY+=zoom*(H/2-lpy);
      }}
    }}
  }}
  // Scale around canvas center then pan
  ctx.save();
  ctx.translate(W/2+panX,H/2+panY);
  ctx.scale(zoom,zoom);
  ctx.translate(-W/2,-H/2);
  return true;
}}

// ─── Main draw ───────────────────────────────────────────────────────────────

function draw(progress){{
  const frame=Math.round(progress*totF);
  const revP=Math.min(frame/revF,1.0);
  const xCur=xS+(xE-xS)*revP;
  const tSec=(frame/fps).toFixed(2);
  const frozen=frame>=(totF-frz);
  const curves=C.reactor_curves||[];
  ctx.clearRect(0,0,W,H);ctx.fillStyle='#0a0a0f';ctx.fillRect(0,0,W,H);
  // Compute y range once (needed for camera follow_asset + drawing)
  const[mn,mx]=geo!=='polar'?yRange(curves,xCur):[0,1];
  // Apply camera transform
  let camApplied=false;
  if(cameraMode&&cam){{camApplied=applyCamTransform(frame,mn,mx);}}
  // Draw scene
  if(geo==='polar'){{curves.forEach(c=>drawPolarCurve(c,xCur));}}
  else{{drawGrid(mn,mx);curves.forEach(c=>drawCartCurve(c,xCur,mn,mx));}}
  // Restore camera before overlay (overlay always in screen space)
  if(camApplied)ctx.restore();
  if(frozen)drawFreezeOverlay();
  inf.textContent=`x=${{xCur.toFixed(3)}} | t=${{tSec}}s | frame ${{frame}}/${{totF}}${{frozen?' [FREEZE]':''}}${{cameraMode?' [CAM]':''}}`;
}}

// ─── Snapshots ───────────────────────────────────────────────────────────────

function generateSnapshots(){{
  if(!cam){{document.getElementById('snapBtn').textContent='[ WARN: camera_plan absent ]';return;}}
  const prevVal=+sld.value;
  const prevCam=cameraMode;
  cameraMode=true;
  const keyFrames=[0,Math.round(totF/2),totF-1];
  const lbls=[
    'DEBUT — f.0',
    `MILIEU — f.${{Math.round(totF/2)}}`,
    `FIN — f.${{totF-1}}`
  ];
  keyFrames.forEach((frame,i)=>{{
    draw(frame/totF);
    const sc=document.getElementById('s'+i);
    sc.getContext('2d').drawImage(cnv,0,0,sc.width,sc.height);
    document.getElementById('l'+i).textContent=lbls[i];
  }});
  cameraMode=prevCam;
  draw(prevVal/1000);
  document.getElementById('snapBtn').textContent='[ REGENERER SNAPSHOTS ]';
  document.getElementById('snapBtn').style.color='#00FFD1';
  document.getElementById('snapBtn').style.borderColor='#00FFD1';
}}

sld.addEventListener('input',()=>draw(sld.value/1000));
draw(0.5);
</script></body></html>"""


# ─── Streamlit UI ──────────────────────────────────────────────────────────────

def render_curve_editor(data, idx):
    c = data["reactor_curves"][idx]
    cid = c.get("id", f"courbe_{idx}")
    with st.expander(f"Courbe {idx+1} — {cid}", expanded=(idx == 0)):
        c["id"] = st.text_input(f"ID #{idx}", value=cid, key=f"cid_{idx}")
        c["math_input"] = st.text_input(
            f"math_input (math.js) #{idx}", value=c.get("math_input", ""),
            key=f"mi_{idx}", help="Ex: 1/(1+exp(-(x-5))) — variables: x ou theta")
        rs = c.setdefault("render_style", {})
        rs["color_hex"] = st.color_picker(f"Couleur #{idx}", value=rs.get("color_hex", "#00FFD1"), key=f"col_{idx}")
        asp = c.setdefault("animation_speed", {})
        cur_rs = asp.get("reveal_style", "linear")
        idx_rs = REVEAL_STYLES.index(cur_rs) if cur_rs in REVEAL_STYLES else 0
        asp["reveal_style"] = st.selectbox(f"reveal_style #{idx}", REVEAL_STYLES, index=idx_rs, key=f"rv_{idx}")
        asp["pace_factor"] = st.slider(f"pace_factor #{idx}", 0.1, 3.0,
                                       float(asp.get("pace_factor", 1.0)), 0.1, key=f"pf_{idx}")
        tt = c.setdefault("tracking_target", {})
        tt["asset_filename"] = st.text_input(f"PNG asset #{idx}", value=tt.get("asset_filename", ""),
                                             key=f"png_{idx}", help="Nom du fichier PNG dans IN/images/")


def render_camera_info(data):
    """Affiche le camera_plan en lecture seule."""
    cam = data.get("camera_plan")
    if not cam:
        st.warning("camera_plan absent — déposer camera_plan.json dans F02/IN/ puis relancer.")
        return
    gs = cam.get("global_style", {})
    st.caption(
        f"Signature : `{cam.get('camera_signature', '?')}` | "
        f"Energy : `{gs.get('movement_energy', '?')}` | "
        f"Easing : `{gs.get('default_easing', '?')}`"
    )
    segs = cam.get("camera_segments", [])
    for s in segs:
        mode_color = {"follow_asset": "🟡", "wide_reveal": "🔵", "final_proof_lock": "🟢"}.get(s["mode"], "⚪")
        st.caption(
            f"{mode_color} Seg frames **{s['start_frame']}–{s['end_frame']}** | "
            f"`{s['mode']}` | zoom `{s['zoom']}` | "
            f"offset ({s.get('x_offset',0)}, {s.get('y_offset',0)}) | "
            f"shake `{s.get('shake',0)}`"
        )


def main():
    base     = get_drive_base()
    in_json  = os.path.join(base, "F02_CASTELLAN", "IN", "plan_de_vol.json")
    in_cam   = os.path.join(base, "F02_CASTELLAN", "IN", "camera_plan.json")
    out_json = os.path.join(base, "F02_CASTELLAN", "OUT", "plan_de_vol.json")

    st.set_page_config(page_title="F02 CASTELLAN — PENTERACT DORN", layout="wide")
    st.markdown("## F02 CASTELLAN — HUD DE CONTRÔLE")
    st.caption("PENTERACT DORN V3 — VIIe Légion | Streamlit + Canvas JS + math.js")
    st.divider()

    # ── Chargement JSON ──────────────────────────────────────────────────────
    if "data" not in st.session_state:
        if not os.path.exists(in_json):
            st.error(f"plan_de_vol.json introuvable : {in_json}")
            st.info("Déposer le fichier dans F02_CASTELLAN/IN/ puis relancer.")
            st.stop()
        plan = load_json(in_json)

        # Merge camera_plan si absent du plan et présent en fichier séparé
        if "camera_plan" not in plan:
            if os.path.exists(in_cam):
                cam_raw = load_json(in_cam)
                # camera_plan.json peut avoir un wrapper {"camera_plan": {...}} ou être direct
                plan["camera_plan"] = cam_raw.get("camera_plan", cam_raw)
                st.session_state.cam_source = "fichier séparé (camera_plan.json)"
            else:
                st.session_state.cam_source = None
        else:
            st.session_state.cam_source = "intégré dans plan_de_vol.json"

        st.session_state.data = plan

    data = st.session_state.data

    # Status caméra
    cam_source = st.session_state.get("cam_source")
    if cam_source:
        st.success(f"camera_plan chargé — source : {cam_source}")
    elif "camera_plan" not in data:
        st.warning("camera_plan absent. Déposer camera_plan.json dans F02/IN/ pour activer la visualisation caméra.")

    col_edit, col_sim = st.columns([1, 1], gap="large")

    # ── Colonne édition ──────────────────────────────────────────────────────
    with col_edit:
        st.markdown("### Métadonnées")
        cm = data.setdefault("concept_metadata", {})
        cm["title"]  = st.text_input("Titre viral", value=cm.get("title", ""), key="title")
        cm["thesis"] = st.text_input("Thèse (bas d'écran)", value=cm.get("thesis", ""), key="thesis")
        cur_fmt = cm.get("format", "vertical")
        cm["format"] = st.radio("Format", FORMATS, index=FORMATS.index(cur_fmt) if cur_fmt in FORMATS else 0,
                                horizontal=True, key="fmt")

        st.markdown("### Espace mathématique")
        se = data.setdefault("space_environment", {})
        se["x_label"] = st.text_input("Label axe X", value=se.get("x_label", "x"), key="xl")
        se["y_label"] = st.text_input("Label axe Y", value=se.get("y_label", "y"), key="yl")
        cur_gm = se.get("geometry_mode", "cartesian")
        se["geometry_mode"] = st.radio("Geometry mode", GEOMETRY_MODES,
                                       index=GEOMETRY_MODES.index(cur_gm) if cur_gm in GEOMETRY_MODES else 0,
                                       horizontal=True, key="gm")

        st.markdown("### Courbes")
        n_curves = len(data.get("reactor_curves", []))
        for i in range(n_curves):
            render_curve_editor(data, i)
        if st.button("+ Ajouter une courbe", key="add_curve"):
            data.setdefault("reactor_curves", []).append({
                "id": f"courbe_{n_curves + 1}",
                "math_input": "sin(x)",
                "render_style": {"color_hex": "#FF3366", "glow_radius_px": 20, "line_width_px": 6},
                "animation_speed": {"reveal_style": "linear", "pace_factor": 1.0},
                "tracking_target": {"asset_filename": "", "scale_factor": 1.2,
                                    "physics": {"auto_rotate_slope": True, "inertia_smooth": 0.1}}
            })
            st.rerun()

        st.markdown("### Final Frame")
        ff = data.setdefault("final_frame", {})
        ff["annotation"] = st.text_input("Annotation finale", value=ff.get("annotation", ""), key="ann")

        st.markdown("### Camera Plan — lecture seule (META_CAMERA)")
        render_camera_info(data)

        st.divider()
        st.markdown("### Timing (lecture seule — modifiable dans plan_de_vol.json)")
        t = data.get("timing", {})
        cols_t = st.columns(3)
        cols_t[0].metric("Durée cible", f"{t.get('target_duration_seconds', '?')}s")
        cols_t[1].metric("FPS", t.get("fps", 60))
        cols_t[2].metric("step_per_frame", t.get("step_per_frame", "?"))

        st.divider()
        # ── FIGER LE PLAN DE VOL ─────────────────────────────────────────────
        st.markdown("### ⚡ Validation finale")
        if "camera_plan" not in data:
            st.error("Impossible de figer : camera_plan manquant. Déposer camera_plan.json dans F02/IN/.")
        else:
            if st.button("FIGER LE PLAN DE VOL", type="primary", use_container_width=True):
                data["validated_by_magos"] = True
                data["validation_timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
                # Aligne freeze_duration_frames sur final_freeze_frames
                data.setdefault("final_frame", {})["freeze_duration_frames"] = \
                    data.get("timing", {}).get("final_freeze_frames", 180)
                save_json(data, out_json)
                st.success(f"Plan de vol figé → {out_json}")
                st.success("validated_by_magos: true | camera_plan inclus | Passer à F03 SIGISMUND.")
                st.balloons()

    # ── Colonne simulation ───────────────────────────────────────────────────
    with col_sim:
        st.markdown("### Simulation Canvas")
        st.caption(
            "Scrubber : parcourir l'animation. "
            "**CAMERA ON** : active le transform caméra en temps réel. "
            "**SNAPSHOTS** : captures aux frames clés avec caméra active."
        )
        canvas_height = 700 if cm.get("format") == "vertical" else 460
        components.html(build_canvas_html(data), height=canvas_height, scrolling=False)

        if data.get("validated_by_magos"):
            ts = data.get("validation_timestamp", "—")
            st.success(f"Plan figé le {ts}")
        else:
            st.info("Vérifier l'animation ci-dessus, valider la caméra, puis FIGER.")


if __name__ == "__main__":
    main()
