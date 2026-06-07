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

Entrées  : F02_CASTELLAN/IN/plan_de_vol.json   (plan sorti de F01 + camera_plan généré par META_POLUX V5)
           F02_CASTELLAN/IN/images/*.png
Sorties  : F02_CASTELLAN/OUT/plan_de_vol.json  (validated_by_magos: true)
"""

import argparse
import base64
import datetime
import json
import os
import sys

import streamlit as st
import streamlit.components.v1 as components

# ─── Configuration ─────────────────────────────────────────────────────────────

DEFAULT_DRIVE_BASE = "/content/drive/MyDrive/DRIVE_DORN"

REVEAL_STYLES   = ["linear", "ease_in", "ease_out", "ease_in_out", "dramatic"]
MOVEMENT_ENERGY = ["calm", "cinematic", "aggressive", "viral_edit"]
GEOMETRY_MODES  = ["cartesian", "polar"]
FORMATS         = ["vertical", "horizontal"]
FONTS           = ["monospace", "serif", "sans-serif"]

# ─── Args ──────────────────────────────────────────────────────────────────────

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
# FIX: JSON injected as base64 via data attribute — bulletproof against any
#      character (emoji, special chars, HTML sequences, surrogates) that would
#      make JSON.parse throw a SyntaxError and leave the canvas black.
# FIX: camera_on parameter persists camera state across Streamlit rerenders.

def build_canvas_html(data, camera_on=False, image_map=None):
    fmt = data.get("concept_metadata", {}).get("format", "vertical")
    cw, ch = (360, 460) if fmt == "vertical" else (560, 300)

    # Base64 — zero HTML-context issue possible
    json_b64 = base64.b64encode(
        json.dumps(data, ensure_ascii=False).encode("utf-8")
    ).decode("ascii")
    imgs_b64 = base64.b64encode(
        json.dumps(image_map or {}, ensure_ascii=False).encode("utf-8")
    ).decode("ascii")
    cam_init = "true" if camera_on else "false"

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjs/11.11.0/math.min.js"></script>
<style>
body{{background:#0a0a0f;color:#ccc;font-family:monospace;margin:0;padding:6px}}
canvas{{display:block;margin:0 auto;background:#0a0a0f}}
#slider{{width:100%;margin:6px 0;accent-color:#00FFD1}}
#info{{text-align:center;font-size:11px;color:#777;margin-bottom:3px}}
#ttl{{text-align:center;font-size:12px;color:#eee;margin-bottom:5px;font-weight:bold}}
#camBtn{{display:block;margin:4px auto;padding:4px 20px;background:#1a1a2e;border:1px solid #333355;color:#555577;font-family:monospace;font-size:11px;letter-spacing:1px;cursor:default;pointer-events:none}}
#camBtn.on{{background:#00FFD1;color:#0a0a0f;font-weight:bold;border-color:#00FFD1}}
#snapBtn{{display:block;margin:8px auto;padding:3px 14px;background:#1a1a2e;border:1px solid #333;color:#555;cursor:pointer;font-family:monospace;font-size:10px}}
.snaps{{display:flex;gap:4px;justify-content:center;margin-top:6px}}
.snap-item{{flex:1;text-align:center}}
.snap-item canvas{{width:100%;height:auto;border:1px solid #1a1a2e;display:block}}
.snap-label{{font-size:9px;color:#444;margin-top:2px}}
#segBar{{font-size:9px;color:#333;text-align:center;margin:3px 0;line-height:1.8}}
</style></head><body>
<meta id="polux-cfg" data-cfg="{json_b64}">
<meta id="polux-imgs" data-imgs="{imgs_b64}">
<div id="ttl"></div>
<canvas id="sim" width="{cw}" height="{ch}"></canvas>
<input type="range" id="slider" min="0" max="1000" value="500">
<div id="info">x=0 | t=0.00s | frame 0</div>
<button id="camBtn">CAMERA : OFF</button>
<div id="segBar"></div>
<button id="snapBtn" onclick="generateSnapshots()">[ GÉNÉRER SNAPSHOTS CAMÉRA ]</button>
<div class="snaps">
  <div class="snap-item"><canvas id="s0" width="{cw}" height="{ch}"></canvas><div class="snap-label" id="l0">—</div></div>
  <div class="snap-item"><canvas id="s1" width="{cw}" height="{ch}"></canvas><div class="snap-label" id="l1">—</div></div>
  <div class="snap-item"><canvas id="s2" width="{cw}" height="{ch}"></canvas><div class="snap-label" id="l2">—</div></div>
</div>
<script>
// Base64 decode — immune to any character that could corrupt HTML script context
const C=JSON.parse(atob(document.getElementById('polux-cfg').dataset.cfg));
const cam=C.camera_plan||null;
const hud=C.hud_config||{{}};
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
// FIX: initialised from Python-side toggle — survives Streamlit rerenders
let cameraMode={cam_init};

// ─── Camera ──────────────────────────────────────────────────────────────────

function updateCamBtn(){{
  const btn=document.getElementById('camBtn');
  btn.textContent='CAMERA : '+(cameraMode?'ON':'OFF');
  btn.className=cameraMode?'on':'';
}}

function getActiveSeg(frame){{
  if(!cam)return null;
  const segs=cam.camera_segments||[];
  for(let s of segs){{if(frame>=s.start_frame&&frame<=s.end_frame)return s;}}
  return segs.length?segs[segs.length-1]:null;
}}

// toggleCam est piloté uniquement par le toggle Streamlit (col_sim).
// Le bouton #camBtn est un indicateur read-only — pas de onclick.
function toggleCam(){{
  updateCamBtn();
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
  curves.forEach(c=>{{sampleCart(c.math_input,xCur).forEach(([,y])=>{{mn=Math.min(mn,y);mx=Math.max(mx,y);}});}});
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

function hexToRgba(hex,alpha){{
  const h=hex.replace('#','');
  const r=parseInt(h.slice(0,2),16),g=parseInt(h.slice(2,4),16),b=parseInt(h.slice(4,6),16);
  return `rgba(${{r}},${{g}},${{b}},${{alpha}})`;
}}

function drawGrid(mn,mx){{
  const gc=hud.grid_color||'#2a2a4a';
  const go=hud.grid_opacity??0.8;
  const glw=hud.grid_line_width||1;
  const alc=hud.axis_label_color||'#aaaaaa';
  const als=hud.axis_label_size_px||12;
  const alf=hud.axis_label_font||'monospace';

  // Cadre de la zone de tracé (toujours visible)
  ctx.strokeStyle='#3a3a5a';ctx.lineWidth=1.5;
  ctx.strokeRect(PL,PT,PW,PHT);

  // Lignes de grille intérieures
  ctx.strokeStyle=hexToRgba(gc,go);ctx.lineWidth=glw;
  for(let i=1;i<=4;i++){{const x=PL+(i/5)*PW;ctx.beginPath();ctx.moveTo(x,PT);ctx.lineTo(x,PT+PHT);ctx.stroke();}}
  for(let i=1;i<=3;i++){{const y=PT+(i/4)*PHT;ctx.beginPath();ctx.moveTo(PL,y);ctx.lineTo(PL+PW,y);ctx.stroke();}}

  // Axes x=0 et y=0 — toujours tracés s'ils sont dans la plage visible
  const axisColor=hud.center_axis_color||'#555580';
  ctx.strokeStyle=axisColor;ctx.lineWidth=1.5;
  const cx=PL+((0-xS)/(xE-xS))*PW;
  if(cx>=PL&&cx<=PL+PW){{ctx.beginPath();ctx.moveTo(cx,PT);ctx.lineTo(cx,PT+PHT);ctx.stroke();}}
  const cy=PT+(1-(0-mn)/(mx-mn))*PHT;
  if(cy>=PT&&cy<=PT+PHT){{ctx.beginPath();ctx.moveTo(PL,cy);ctx.lineTo(PL+PW,cy);ctx.stroke();}}

  // Labels axes
  ctx.fillStyle=alc;ctx.font=`${{als}}px ${{alf}}`;ctx.textAlign='center';
  for(let i=0;i<=5;i++)ctx.fillText((xS+(i/5)*(xE-xS)).toFixed(1),PL+(i/5)*PW,PT+PHT+16);
  ctx.textAlign='right';
  for(let i=0;i<=4;i++)ctx.fillText((mx-(i/4)*(mx-mn)).toFixed(2),PL-6,PT+(i/4)*PHT+4);

  // Titres des axes
  ctx.fillStyle=alc;ctx.font=`${{als}}px ${{alf}}`;ctx.textAlign='center';
  ctx.fillText(C.space_environment?.x_label||'x',W/2,H-4);
  ctx.save();ctx.translate(13,H/2);ctx.rotate(-Math.PI/2);
  ctx.fillText(C.space_environment?.y_label||'y',0,0);ctx.restore();
}}

function drawCartCurve(c,xCur,mn,mx){{
  const pts=sampleCart(c.math_input,xCur);if(pts.length<2)return null;
  const col=c.render_style?.color_hex||'#00FFD1';
  const glo=c.render_style?.glow_radius_px??20;
  const lw=c.render_style?.line_width_px??6;
  ctx.save();ctx.shadowBlur=glo;ctx.shadowColor=col;
  ctx.strokeStyle=col;ctx.lineWidth=lw;ctx.lineJoin='round';ctx.lineCap='round';
  ctx.beginPath();
  pts.forEach(([xv,yv],i)=>{{const[px,py]=toXY(xv,yv,mn,mx);i===0?ctx.moveTo(px,py):ctx.lineTo(px,py);}});
  ctx.stroke();ctx.restore();
  const[lx,ly]=toXY(pts[pts.length-1][0],pts[pts.length-1][1],mn,mx);
  ctx.save();ctx.shadowBlur=glo*1.5;ctx.shadowColor=col;ctx.fillStyle='#fff';
  ctx.beginPath();ctx.arc(lx,ly,5,0,Math.PI*2);ctx.fill();ctx.restore();
  if(c.render_style?.show_equation_label!==false){{
    const elc=c.render_style?.equation_label_color||'#FFFFFF';
    const els=c.render_style?.equation_label_size_px||11;
    const elf=c.render_style?.equation_label_font||'monospace';
    ctx.save();
    ctx.fillStyle=elc;ctx.font=`${{els}}px ${{elf}}`;ctx.textAlign='left';
    ctx.shadowBlur=4;ctx.shadowColor='#000000';
    ctx.fillText(c.math_input||'',lx+8,ly-8);
    ctx.restore();
  }}
  const tt=c.tracking_target;
  if(tt?.show_asset&&tt.asset_filename&&imgMap[tt.asset_filename]){{
    const img=imgMap[tt.asset_filename];
    const sc=Math.max(0.3,Math.min(tt.scale_factor??1.2,3.0));
    const ih=50*sc,iw=(img.naturalWidth/Math.max(img.naturalHeight,1))*ih;
    ctx.save();ctx.globalAlpha=0.9;
    ctx.drawImage(img,lx-iw/2,ly-ih/2,iw,ih);
    ctx.restore();
  }}
  return[lx,ly];
}}

function drawPolarCurve(c,tCur){{
  const pts=samplePolar(c.math_input,tCur);if(pts.length<2)return;
  const rMax=Math.max(...pts.map(([r])=>Math.abs(r)))||1;
  const col=c.render_style?.color_hex||'#00FFD1';
  const glo=c.render_style?.glow_radius_px??20;
  const lw=c.render_style?.line_width_px??6;
  ctx.save();ctx.shadowBlur=glo;ctx.shadowColor=col;
  ctx.strokeStyle=col;ctx.lineWidth=lw;ctx.lineJoin='round';
  ctx.beginPath();
  pts.forEach(([r,th],i)=>{{const[px,py]=toPolar(r,th,rMax);i===0?ctx.moveTo(px,py):ctx.lineTo(px,py);}});
  ctx.stroke();ctx.restore();
}}

function drawFreezeOverlay(){{
  const ff=C.final_frame||{{}};
  const ann=ff.annotation||'';
  const annc=ff.annotation_color||'#FFD700';
  const anns=ff.annotation_size_px||14;
  const annf=ff.annotation_font||'monospace';
  ctx.save();
  ctx.fillStyle='rgba(0,0,0,0.55)';ctx.fillRect(PL,PT+PHT*0.6,PW,PHT*0.32);
  ctx.fillStyle=annc;ctx.font=`bold ${{anns}}px ${{annf}}`;ctx.textAlign='center';
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
  const[mn,mx]=geo!=='polar'?yRange(curves,xCur):[0,1];
  const axesWorld=hud.axes_world_space||false;
  let camApplied=false;
  if(cameraMode&&cam){{
    if(axesWorld){{
      camApplied=applyCamTransform(frame,mn,mx);
      if(geo==='polar'){{curves.forEach(c=>drawPolarCurve(c,xCur));}}
      else{{drawGrid(mn,mx);curves.forEach(c=>drawCartCurve(c,xCur,mn,mx));}}
      if(camApplied)ctx.restore();
    }}else{{
      if(geo!=='polar')drawGrid(mn,mx);
      camApplied=applyCamTransform(frame,mn,mx);
      if(geo==='polar'){{curves.forEach(c=>drawPolarCurve(c,xCur));}}
      else{{curves.forEach(c=>drawCartCurve(c,xCur,mn,mx));}}
      if(camApplied)ctx.restore();
    }}
  }}else{{
    if(geo==='polar'){{curves.forEach(c=>drawPolarCurve(c,xCur));}}
    else{{drawGrid(mn,mx);curves.forEach(c=>drawCartCurve(c,xCur,mn,mx));}}
  }}
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
  const lbls=['DEBUT — f.0',`MILIEU — f.${{Math.round(totF/2)}}`,`FIN — f.${{totF-1}}`];
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

// ─── Image preload ────────────────────────────────────────────────────────────
const imgData=JSON.parse(atob(document.getElementById('polux-imgs').dataset.imgs));
const imgMap={{}};
function preloadImages(){{
  const entries=Object.entries(imgData);
  if(!entries.length){{bootCanvas();return;}}
  let rem=entries.length;
  entries.forEach(([name,uri])=>{{
    const img=new Image();
    img.onload=img.onerror=()=>{{imgMap[name]=img;rem--;if(!rem)bootCanvas();}};
    img.src=uri;
  }});
}}
// ─── Init ────────────────────────────────────────────────────────────────────
function bootCanvas(){{
  updateCamBtn();
  sld.addEventListener('input',()=>draw(sld.value/1000));
  draw(0.5);
}}
preloadImages();
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
        rs["glow_radius_px"] = st.slider(f"Glow (halo) #{idx}", 0, 60, int(rs.get("glow_radius_px", 20)), 1, key=f"glo_{idx}")
        rs["line_width_px"] = st.slider(f"Épaisseur ligne #{idx}", 1, 15, int(rs.get("line_width_px", 6)), 1, key=f"lw_{idx}")

        with st.expander(f"Équation label #{idx}", expanded=False):
            rs["show_equation_label"] = st.toggle(
                f"Afficher équation #{idx}", value=rs.get("show_equation_label", True), key=f"sel_{idx}")
            if rs["show_equation_label"]:
                rs["equation_label_color"] = st.color_picker(
                    f"Couleur équation #{idx}", value=rs.get("equation_label_color", "#FFFFFF"), key=f"elc_{idx}")
                rs["equation_label_size_px"] = st.slider(
                    f"Taille équation #{idx}", 8, 18, int(rs.get("equation_label_size_px", 11)), 1, key=f"els_{idx}")
                cur_elf = rs.get("equation_label_font", "monospace")
                rs["equation_label_font"] = st.selectbox(
                    f"Police équation #{idx}", FONTS,
                    index=FONTS.index(cur_elf) if cur_elf in FONTS else 0, key=f"elf_{idx}")

        tt = c.setdefault("tracking_target", {})
        with st.expander(f"Image asset #{idx}", expanded=False):
            tt["show_asset"] = st.toggle(
                f"Afficher image #{idx}", value=tt.get("show_asset", True), key=f"sa_{idx}")
            tt["asset_filename"] = st.text_input(
                f"Nom fichier #{idx}", value=tt.get("asset_filename", ""),
                key=f"png_{idx}", help="Nom du fichier PNG/JPEG dans IN/images/")
            tt["scale_factor"] = st.slider(
                f"Taille PNG (scale F03) #{idx}", 0.3, 3.0, float(tt.get("scale_factor", 1.2)), 0.1, key=f"sf_{idx}")

        asp = c.setdefault("animation_speed", {})
        cur_rs = asp.get("reveal_style", "linear")
        idx_rs = REVEAL_STYLES.index(cur_rs) if cur_rs in REVEAL_STYLES else 0
        asp["reveal_style"] = st.selectbox(f"reveal_style #{idx}", REVEAL_STYLES, index=idx_rs, key=f"rv_{idx}")
        asp["pace_factor"] = st.slider(f"pace_factor #{idx}", 0.1, 3.0,
                                       float(asp.get("pace_factor", 1.0)), 0.1, key=f"pf_{idx}")


def main():
    base     = get_drive_base()
    in_json  = os.path.join(base, "F02_CASTELLAN", "IN", "plan_de_vol.json")
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
        st.session_state.data = load_json(in_json)

    data = st.session_state.data

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

        st.markdown("### Grille & Axes")
        hud = data.setdefault("hud_config", {})
        hud["grid_color"] = st.color_picker("Couleur grille", value=hud.get("grid_color", "#2a2a4a"), key="gc")
        hud["grid_opacity"] = st.slider("Opacité grille", 0.0, 1.0, float(hud.get("grid_opacity", 1.0)), 0.05, key="go")
        hud["grid_line_width"] = st.slider("Épaisseur lignes grille", 0.5, 3.0, float(hud.get("grid_line_width", 1.0)), 0.5, key="glw")
        hud["axis_label_color"] = st.color_picker("Couleur labels axes", value=hud.get("axis_label_color", "#888888"), key="alc")
        hud["axis_label_size_px"] = st.slider("Taille labels axes", 8, 16, int(hud.get("axis_label_size_px", 10)), 1, key="als")
        cur_alf = hud.get("axis_label_font", "monospace")
        hud["axis_label_font"] = st.selectbox("Police labels axes", FONTS,
                                              index=FONTS.index(cur_alf) if cur_alf in FONTS else 0, key="alf")
        hud["show_center_axis"] = st.toggle("Axe central visible", value=hud.get("show_center_axis", False), key="sca")
        if hud["show_center_axis"]:
            hud["center_axis_color"] = st.color_picker("Couleur axe central",
                                                        value=hud.get("center_axis_color", "#333355"), key="cac")
        else:
            hud.setdefault("center_axis_color", "#333355")
        hud["axes_world_space"] = st.toggle(
            "Axes en world space", value=hud.get("axes_world_space", False), key="aws",
            help="OFF = grille fixe screen space (recommandé). ON = grille zoome avec la caméra.")

        st.markdown("### Courbes")
        n_curves = len(data.get("reactor_curves", []))
        for i in range(n_curves):
            render_curve_editor(data, i)
        if st.button("+ Ajouter une courbe", key="add_curve"):
            data.setdefault("reactor_curves", []).append({
                "id": f"courbe_{n_curves + 1}",
                "math_input": "sin(x)",
                "render_style": {
                    "color_hex": "#FF3366",
                    "glow_radius_px": 20,
                    "line_width_px": 6,
                    "show_equation_label": True,
                    "equation_label_color": "#FFFFFF",
                    "equation_label_size_px": 11,
                    "equation_label_font": "monospace"
                },
                "animation_speed": {"reveal_style": "linear", "pace_factor": 1.0},
                "tracking_target": {
                    "show_asset": True,
                    "asset_filename": "",
                    "scale_factor": 1.2,
                    "physics": {"auto_rotate_slope": True, "inertia_smooth": 0.1}
                }
            })
            st.rerun()

        st.markdown("### Final Frame")
        ff = data.setdefault("final_frame", {})
        ff["annotation"] = st.text_input("Texte annotation", value=ff.get("annotation", ""), key="ann")
        ff["annotation_color"] = st.color_picker("Couleur annotation",
                                                  value=ff.get("annotation_color", "#FFD700"), key="annc")
        ff["annotation_size_px"] = st.slider("Taille annotation", 10, 28,
                                             int(ff.get("annotation_size_px", 14)), 1, key="anns")
        cur_annf = ff.get("annotation_font", "monospace")
        ff["annotation_font"] = st.selectbox("Police annotation", FONTS,
                                             index=FONTS.index(cur_annf) if cur_annf in FONTS else 0, key="annf")
        ff["freeze_duration_frames"] = st.slider("Durée freeze (frames)", 60, 360,
                                                  int(ff.get("freeze_duration_frames", 90)), 10, key="fdf")

        st.markdown("### Camera Plan")
        cam_data = data.get("camera_plan")
        cam_json_on = st.toggle("Inclure camera_plan dans le JSON", value=bool(cam_data), key="cam_json_on")
        if cam_json_on:
            if not cam_data:
                data["camera_plan"] = {
                    "global_style": {
                        "movement_energy": "cinematic",
                        "shake_intensity": 0.05,
                        "default_easing": "ease_in_out"
                    },
                    "camera_segments": []
                }
                cam_data = data["camera_plan"]
            gs = cam_data.setdefault("global_style", {})
            cur_me = gs.get("movement_energy", "cinematic")
            gs["movement_energy"] = st.selectbox(
                "movement_energy", MOVEMENT_ENERGY,
                index=MOVEMENT_ENERGY.index(cur_me) if cur_me in MOVEMENT_ENERGY else 1, key="me")
            gs["shake_intensity"] = st.slider(
                "shake_intensity global", 0.0, 0.15, float(gs.get("shake_intensity", 0.05)), 0.01, key="si")
            segs_json = json.dumps(cam_data.get("camera_segments", []), indent=2, ensure_ascii=False)
            new_segs_json = st.text_area("Segments caméra (JSON brut)", value=segs_json,
                                         height=200, key="segs_json")
            try:
                cam_data["camera_segments"] = json.loads(new_segs_json)
            except json.JSONDecodeError as e:
                st.error(f"JSON invalide dans les segments : {e}")
        else:
            data.pop("camera_plan", None)

        st.divider()
        st.markdown("### Timing (lecture seule — modifiable dans plan_de_vol.json)")
        t = data.get("timing", {})
        cols_t = st.columns(3)
        cols_t[0].metric("Durée cible", f"{t.get('target_duration_seconds', '?')}s")
        cols_t[1].metric("FPS", t.get("fps", 60))
        cols_t[2].metric("step_per_frame", t.get("step_per_frame", "?"))

        st.divider()
        st.markdown("### Validation finale")
        if st.button("FIGER LE PLAN DE VOL", type="primary", use_container_width=True):
            data["validated_by_magos"] = True
            data["validation_timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
            data.setdefault("final_frame", {})["freeze_duration_frames"] = \
                ff.get("freeze_duration_frames",
                       data.get("timing", {}).get("final_freeze_frames", 180))
            save_json(data, out_json)
            st.success(f"Plan de vol figé → {out_json}")
            st.success("validated_by_magos: true | Passer à F03 SIGISMUND.")
            st.balloons()

    # ── Colonne simulation ───────────────────────────────────────────────────
    with col_sim:
        st.markdown("### Simulation Canvas")
        st.caption(
            "Scrubber : parcourir l'animation. "
            "Toggle **CAMÉRA ON** ci-dessous = seul contrôle caméra (stable entre rerenders). "
            "L'indicateur dans le canvas est en lecture seule. "
            "**SNAPSHOTS** : captures aux frames clés."
        )

        # FIX: camera state stored in session_state → survives Streamlit rerenders
        cam_preview = st.toggle(
            "CAMÉRA ON",
            value=st.session_state.get("cam_preview_state", False),
            key="cam_preview_state",
            help="Stable entre les rerenders. Correspond au bouton CAMERA dans le canvas."
        )

        canvas_height = 700 if cm.get("format") == "vertical" else 460
        images_dir = os.path.join(base, "F02_CASTELLAN", "IN", "images")
        image_map: dict = {}
        for c in data.get("reactor_curves", []):
            tt = c.get("tracking_target", {})
            if tt.get("show_asset") and tt.get("asset_filename"):
                fname = tt["asset_filename"]
                if fname not in image_map:
                    fpath = os.path.join(images_dir, fname)
                    if os.path.exists(fpath):
                        with open(fpath, "rb") as img_f:
                            raw = img_f.read()
                        ext = fname.rsplit(".", 1)[-1].lower()
                        mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
                        image_map[fname] = (
                            f"data:{mime};base64,"
                            + base64.b64encode(raw).decode("ascii")
                        )
        components.html(build_canvas_html(data, cam_preview, image_map), height=canvas_height, scrolling=False)

        if data.get("validated_by_magos"):
            ts = data.get("validation_timestamp", "—")
            st.success(f"Plan figé le {ts}")
        else:
            st.info("Vérifier l'animation ci-dessus, valider la caméra, puis FIGER.")


if __name__ == "__main__":
    main()



