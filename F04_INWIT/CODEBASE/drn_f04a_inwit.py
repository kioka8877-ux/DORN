"""
DRN F04A INWIT — Viewer HTML + Sélecteur Vitesse
PENTERACT DORN V3 — VIIe Légion

Rôle : Afficher video_render.mp4 dans Colab, permettre à l'opérateur
       de choisir la vitesse de lecture, figer le choix vers F04B.

Entrées  : F04_INWIT/IN/video_render.mp4 + F04_INWIT/IN/plan_de_vol.json
Sorties  : F04_INWIT/OUT/speed_validated.json
           F04_INWIT/OUT/plan_de_vol.json (avec playback_speed mis à jour)
"""

import argparse
import base64
import json
import sys
from pathlib import Path

DEFAULT_DRIVE_BASE = "/content/drive/MyDrive/DRIVE_DORN"

# ─────────────────────────────────────────────────────────────────────────────
def log(msg: str):
    print(f"[DRN-F04A] {msg}", flush=True)


def paths(drive_base: str) -> dict:
    base = Path(drive_base) / "F04_INWIT"
    return {
        "in":    base / "IN",
        "out":   base / "OUT",
        "video": base / "IN" / "video_render.mp4",
        "plan":  base / "IN" / "plan_de_vol.json",
        "speed": base / "OUT" / "speed_validated.json",
    }


def load_plan(plan_path: Path) -> dict:
    with open(plan_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────────────────
# Viewer HTML interactif (Colab uniquement)
# Utilise google.colab.kernel.invokeFunction pour renvoyer la vitesse à Python
# ─────────────────────────────────────────────────────────────────────────────
def display_viewer(video_path: Path, plan: dict, p: dict):
    try:
        from IPython.display import display, HTML
        from google.colab import output
    except ImportError:
        log("ERREUR : ce script doit être exécuté dans Google Colab")
        sys.exit(1)

    meta          = plan.get("concept_metadata", {})
    timing        = plan.get("timing", {})
    current_speed = timing.get("playback_speed", 1.0)
    title         = meta.get("title", "DORN")
    fmt           = meta.get("format", "vertical")
    fps           = timing.get("fps", 60)

    # Durée estimée
    total_frames = (
        (timing.get("x_range", {}).get("end", 20) - timing.get("x_range", {}).get("start", 0))
        / max(timing.get("step_per_frame", 0.05), 1e-9)
        * timing.get("complexity_coefficient", 1.0)
        + timing.get("final_freeze_frames", 180)
    )
    duration_s = total_frames / max(fps, 1)
    duration_display = f"{int(duration_s // 60):02d}:{int(duration_s % 60):02d}"

    # Callback Python — déclenché par le bouton JS "FIGER"
    p["out"].mkdir(parents=True, exist_ok=True)

    def validate_speed(speed_str: str):
        speed = float(speed_str)
        # Écrire speed_validated.json
        with open(p["speed"], "w") as f:
            json.dump({"playback_speed": speed, "validated": True}, f, indent=2)
        # Mettre à jour plan_de_vol.json dans OUT/
        plan["timing"]["playback_speed"] = speed
        plan_out = p["out"] / "plan_de_vol.json"
        with open(plan_out, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        note = "aucun re-encode" if speed == 1.0 else f"re-encode FFmpeg (setpts=PTS/{speed})"
        log(f"Vitesse validee : {speed}x  ({note})")
        log(f"→ {p['speed']}")
        log(f"→ {plan_out}")

    output.register_callback("drn_f04a.validate_speed", validate_speed)

    # Encodage vidéo en base64 (inline HTML)
    log("Encodage de la vidéo pour affichage...")
    vid_b64 = base64.b64encode(video_path.read_bytes()).decode()
    log(f"Vidéo chargée ({video_path.stat().st_size // (1024*1024)} MB)")

    # Dimensions affichage
    vid_w = 280 if fmt == "vertical" else 480
    vid_h = 498 if fmt == "vertical" else 270

    # Génération des boutons de vitesse
    speeds = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]

    def btn_style(s):
        active = s == current_speed
        return (
            f"padding:10px 16px;margin:3px;cursor:pointer;"
            f"border-radius:4px;font-family:monospace;font-size:13px;font-weight:bold;"
            f"border:1px solid #FFD700;"
            f"background:{'#FFD700' if active else '#111'};"
            f"color:{'#000' if active else '#FFD700'};"
        )

    btns_html = "".join(
        f'<button onclick="selectSpeed({s})" id="spdbtn{str(s).replace(".", "_")}" style="{btn_style(s)}">'
        f"{s}x</button>"
        for s in speeds
    )

    html = f"""
<div style="font-family:'Courier New',monospace;background:#060606;color:#ccc;
            padding:24px;border:1px solid #2a2a2a;border-radius:8px;max-width:620px;">

  <!-- Header -->
  <div style="font-size:10px;color:#444;letter-spacing:3px;margin-bottom:6px;">
    PENTERACT DORN V3 — VIIe LÉGION — F04A INWIT
  </div>
  <h2 style="margin:0 0 4px 0;color:#fff;font-size:17px;letter-spacing:1px;">{title}</h2>
  <div style="font-size:11px;color:#555;margin-bottom:18px;">
    Format&nbsp;:&nbsp;<b style="color:#888">{fmt.upper()}</b>
    &nbsp;|&nbsp;{fps}&nbsp;fps
    &nbsp;|&nbsp;Durée&nbsp;estimée&nbsp;:&nbsp;<b style="color:#888">{duration_display}</b>
  </div>

  <!-- Lecteur vidéo -->
  <div style="border:1px solid #1a1a1a;border-radius:4px;overflow:hidden;
              margin-bottom:20px;display:inline-block;vertical-align:top;">
    <video id="dorn_vid" width="{vid_w}" height="{vid_h}" controls
           style="display:block;background:#000;">
      <source src="data:video/mp4;base64,{vid_b64}" type="video/mp4">
    </video>
  </div>

  <!-- Sélecteur vitesse -->
  <div style="margin-bottom:18px;">
    <div style="font-size:10px;color:#555;letter-spacing:2px;margin-bottom:10px;">
      VITESSE DE LECTURE
    </div>
    <div id="speed_btns">{btns_html}</div>
  </div>

  <!-- Indicateur vitesse courante -->
  <div style="margin-bottom:18px;font-size:13px;color:#666;">
    Sélection&nbsp;:&nbsp;
    <span id="sel_speed" style="color:#FFD700;font-weight:bold;">{current_speed}x</span>
    &nbsp;
    <span id="sel_note" style="color:#444;font-size:11px;">
      {'(aucun re-encode)' if current_speed == 1.0 else f'(re-encode FFmpeg setpts=PTS/{current_speed})'}
    </span>
  </div>

  <!-- Bouton FIGER -->
  <button onclick="figerVitesse()"
          style="padding:14px 44px;background:#FFD700;color:#000;border:none;
                 border-radius:4px;font-family:monospace;font-size:15px;
                 font-weight:bold;cursor:pointer;letter-spacing:2px;">
    FIGER LA VITESSE
  </button>

  <div id="figer_msg" style="margin-top:14px;color:#00cc66;font-size:12px;
                              letter-spacing:1px;display:none;">
    ✓ Vitesse figée — passer à la cellule CRS_CUSTOS
  </div>
</div>

<script>
  var selectedSpeed = {current_speed};

  function selectSpeed(s) {{
    selectedSpeed = s;
    document.getElementById('dorn_vid').playbackRate = s;
    document.getElementById('sel_speed').textContent = s + 'x';
    document.getElementById('sel_note').textContent  =
      (s === 1.0) ? '(aucun re-encode)' : '(re-encode FFmpeg setpts=PTS/' + s + ')';

    document.querySelectorAll('#speed_btns button').forEach(function(b) {{
      var active = (b.textContent.trim() === s + 'x');
      b.style.background = active ? '#FFD700' : '#111';
      b.style.color      = active ? '#000'    : '#FFD700';
    }});
  }}

  function figerVitesse() {{
    google.colab.kernel.invokeFunction(
      'drn_f04a.validate_speed', [String(selectedSpeed)], {{}}
    );
    document.getElementById('figer_msg').style.display = 'block';
  }}
</script>
"""

    display(HTML(html))
    log(f"Viewer lancé — vitesse courante : {current_speed}x")
    log("Sélectionner la vitesse puis cliquer  FIGER LA VITESSE")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRÉE PRINCIPALE
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="DRN F04A INWIT — Viewer + Speed selector")
    parser.add_argument("--drive-base", default=DEFAULT_DRIVE_BASE)
    args = parser.parse_args()

    log("=" * 62)
    log("DRN F04A INWIT — Viewer de validation vitesse")
    log("=" * 62)

    p = paths(args.drive_base)

    if not p["video"].exists():
        log(f"ERREUR : vidéo introuvable → {p['video']}")
        log("Vérifier que F03 SIGISMUND a bien généré video_render.mp4")
        sys.exit(1)

    if not p["plan"].exists():
        log(f"ERREUR : plan_de_vol.json introuvable → {p['plan']}")
        sys.exit(1)

    plan = load_plan(p["plan"])
    display_viewer(p["video"], plan, p)


if __name__ == "__main__":
    main()
