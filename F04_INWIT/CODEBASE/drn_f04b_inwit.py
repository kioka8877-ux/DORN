"""
DRN F04B INWIT — FFmpeg Finishing + Camouflage HELBRECHT
PENTERACT DORN V3 — VIIe Légion

Role : Appliquer vitesse validee + camouflage metadata, produire le fichier
       youtube_*.mp4 final pret pour upload.

Entrees  : F04_INWIT/IN/video_render.mp4
           F04_INWIT/OUT/speed_validated.json  (produit par F04A)
           F04_INWIT/OUT/plan_de_vol.json       (produit par F04A)

Sorties  : F04_INWIT/OUT/youtube_short.mp4  (si format=vertical)
           F04_INWIT/OUT/youtube_long.mp4   (si format=horizontal)
           F04_INWIT/OUT/rapport_f04.html   (rapport QA)

Logique camouflage HELBRECHT (V4) :
  Toujours re-encode (meme si speed=1.0) pour :
    - map_metadata -1   : wipe integral des metadonnees
    - libx264 CRF 18    : qualite quasi-lossless
    - loudnorm -14 LUFS : standard YouTube (si audio present)
    - +faststart        : MOOV atom en tete
    - QA gate post-rendu : verification tags suspects + codec + taille
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

DEFAULT_DRIVE_BASE = "/content/drive/MyDrive/DRIVE_DORN"

SUSPICIOUS_TAGS = ("remotion", "opencv", "python", "openai", "runway",
                   "stable-diffusion", "lavf", "lavc", "moviepy")

# ─────────────────────────────────────────────────────────────────────────────
def log(msg: str):
    print(f"[DRN-F04B] {msg}", flush=True)


def paths(drive_base: str) -> dict:
    base = Path(drive_base) / "F04_INWIT"
    return {
        "in":    base / "IN",
        "out":   base / "OUT",
        "video": base / "IN"  / "video_render.mp4",
        "speed": base / "OUT" / "speed_validated.json",
        "plan":  base / "OUT" / "plan_de_vol.json",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Detection des flux audio via ffprobe
# ─────────────────────────────────────────────────────────────────────────────
def has_audio_stream(video_path: Path) -> bool:
    r = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-select_streams", "a",
            "-show_entries", "stream=codec_type",
            "-of", "csv=p=0",
            str(video_path),
        ],
        capture_output=True,
        text=True,
    )
    return bool(r.stdout.strip())


# ─────────────────────────────────────────────────────────────────────────────
# Construction du filtre atempo (gere les valeurs hors 0.5-2.0 par chainage)
# ─────────────────────────────────────────────────────────────────────────────
def build_atempo(speed: float) -> str:
    if 0.5 <= speed <= 2.0:
        return f"atempo={speed}"
    filters = []
    s = speed
    while s > 2.0:
        filters.append("atempo=2.0")
        s /= 2.0
    while s < 0.5:
        filters.append("atempo=0.5")
        s *= 2.0
    filters.append(f"atempo={round(s, 6)}")
    return ",".join(filters)


# ─────────────────────────────────────────────────────────────────────────────
# Commande FFmpeg avec camouflage universel HELBRECHT
# ─────────────────────────────────────────────────────────────────────────────
def build_camouflage_cmd(video_in: Path, video_out: Path, meta: dict, speed: float, audio: bool) -> list:
    """
    Construit la commande FFmpeg avec camouflage universel.
    Patterns herites de CRUSADER F04 HELBRECHT :
      - map_metadata -1 : wipe integral metadonnees
      - libx264 CRF 18  : qualite quasi-lossless
      - GOP 2s          : structure standard
      - yuv420p         : compatibilite max
      - loudnorm -14 LUFS : standard YouTube
      - +faststart      : MOOV atom en tete
      - Tags propres    : title + date uniquement
    """
    title = meta.get("title", "DORN")
    dt    = meta.get("date", date.today().isoformat())
    fps   = int(meta.get("fps", 60))
    gop   = fps * 2

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_in),
        "-map_metadata", "-1",
        "-metadata", "encoder=",
    ]

    # Video filter (setpts si speed != 1.0)
    vf_parts = []
    if speed != 1.0:
        vf_parts.append(f"setpts=PTS/{speed}")

    if vf_parts:
        cmd += ["-vf", ",".join(vf_parts)]

    # Video codec
    cmd += [
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "fast",
        "-profile:v", "high",
        "-level", "4.0",
        "-g", str(gop),
        "-keyint_min", str(gop),
        "-pix_fmt", "yuv420p",
    ]

    # Audio
    if audio:
        af_parts = []
        if speed != 1.0:
            af_parts.append(build_atempo(speed))
        af_parts.append("loudnorm=I=-14:TP=-1:LRA=11")
        cmd += [
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "48000",
            "-ac", "2",
            "-af", ",".join(af_parts),
        ]
    else:
        cmd += ["-an"]

    # Container
    cmd += [
        "-movflags", "+faststart",
        "-metadata", f"title={title}",
        "-metadata", f"date={dt}",
        str(video_out),
    ]

    return cmd


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline FFmpeg — camouflage universel V4
# ─────────────────────────────────────────────────────────────────────────────
def run_ffmpeg(video_in: Path, video_out: Path, speed: float, audio: bool, meta: dict) -> int:
    """Lance FFmpeg avec camouflage universel (toujours re-encode)."""
    cmd = build_camouflage_cmd(video_in, video_out, meta, speed, audio)
    log(f"Mode : CAMOUFLAGE (speed={speed}x, audio={'oui' if audio else 'non'})")
    log(f"CMD : {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


# ─────────────────────────────────────────────────────────────────────────────
# QA gate post-rendu
# ─────────────────────────────────────────────────────────────────────────────
def qa_gate(video_path: Path):
    """Verifie la sortie : tags suspects, codec, taille."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", "-show_streams", str(video_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return False, "ffprobe echoue"

    data = json.loads(result.stdout)
    fmt  = data.get("format", {})
    tags = fmt.get("tags", {})

    issues = []

    all_tags = " ".join(str(v).lower() for v in tags.values())
    for suspect in SUSPICIOUS_TAGS:
        if suspect in all_tags:
            issues.append(f"Tag suspect detecte : '{suspect}'")

    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video":
            if stream.get("codec_name", "").lower() not in ("h264", "avc"):
                issues.append(f"Codec video non H264 : {stream.get('codec_name')}")

    size = int(fmt.get("size", 0))
    if size < 100_000:
        issues.append(f"Fichier trop petit : {size} bytes")

    if issues:
        for i in issues:
            log(f"QA FAIL : {i}")
        return False, issues
    return True, "OK"


# ─────────────────────────────────────────────────────────────────────────────
# Rapport HTML
# ─────────────────────────────────────────────────────────────────────────────
def generate_rapport_html(output_dir: str, meta: dict, video_out: Path, speed: float, qa_result: tuple):
    """Genere rapport_f04.html avec infos de production."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", "-show_streams", str(video_out)],
        capture_output=True, text=True,
    )
    info     = json.loads(result.stdout) if result.returncode == 0 else {}
    fmt_data = info.get("format", {})
    duration = float(fmt_data.get("duration", 0))
    size_mb  = int(fmt_data.get("size", 0)) / (1024 * 1024)

    width = height = 0
    for s in info.get("streams", []):
        if s.get("codec_type") == "video":
            width, height = s.get("width", 0), s.get("height", 0)

    title    = meta.get("title", "DORN")
    fmt_type = "vertical" if height > width else "horizontal"
    out_name = video_out.name

    html = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8">
<title>F04 INWIT — Rapport</title>
<style>
body{{font-family:monospace;background:#0a0a0a;color:#ccc;padding:40px;max-width:700px;margin:0 auto}}
h1{{color:#FFD700;font-size:18px}}
.metric{{background:#111;padding:12px;margin:8px 0;border:1px solid #222;border-radius:4px}}
.ok{{color:#2ecc71}} .fail{{color:#e74c3c}}
</style></head><body>
<h1>F04 INWIT — Rapport de production</h1>
<div class="metric">Fichier : <b>{out_name}</b></div>
<div class="metric">Titre : {title}</div>
<div class="metric">Format : {fmt_type.upper()} ({width}x{height})</div>
<div class="metric">Duree : {duration:.1f}s</div>
<div class="metric">Taille : {size_mb:.1f} MB</div>
<div class="metric">Vitesse : {speed}x</div>
<div class="metric">Camouflage : map_metadata -1, loudnorm -14 LUFS, faststart</div>
<div class="metric {'ok' if qa_result[0] else 'fail'}">
QA : {'PASS' if qa_result[0] else 'FAIL — ' + str(qa_result[1])}</div>
</body></html>"""

    rapport_path = Path(output_dir) / "rapport_f04.html"
    rapport_path.write_text(html, encoding="utf-8")
    log(f"Rapport HTML → {rapport_path}")


# ─────────────────────────────────────────────────────────────────────────────
# ENTREE PRINCIPALE
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="DRN F04B INWIT — FFmpeg Finishing")
    parser.add_argument("--drive-base", default=DEFAULT_DRIVE_BASE)
    parser.add_argument(
        "--speed", type=float, default=None,
        help=(
            "Vitesse de lecture override (ex: 0.5 = moitie, 2.0 = double). "
            "Si fourni, speed_validated.json et plan_de_vol.json (OUT) ne sont pas requis."
        ),
    )
    args = parser.parse_args()

    log("=" * 62)
    log("DRN F04B INWIT — FFmpeg Finishing + Camouflage HELBRECHT")
    log("=" * 62)

    p = paths(args.drive_base)

    # Verification des entrees obligatoires
    if not p["video"].exists():
        log("ERREUR : video_render.mp4 (F03 OUT -> F04 IN)")
        log(f"         introuvable -> {p['video']}")
        sys.exit(1)
    log("OK : video_render.mp4")

    # Vitesse : --speed override OU speed_validated.json
    if args.speed is not None:
        speed = args.speed
        log(f"Vitesse forcee (--speed) : {speed}x")
    else:
        if not p["speed"].exists():
            log("ERREUR : speed_validated.json (F04A OUT) introuvable.")
            log("         Utiliser --speed <valeur> pour bypasser F04A.")
            sys.exit(1)
        with open(p["speed"], encoding="utf-8") as f:
            sv = json.load(f)
        speed = float(sv["playback_speed"])
        log(f"Vitesse figee (speed_validated.json) : {speed}x")

    # Plan : OUT/plan_de_vol.json (F04A) ou IN/plan_de_vol.json (F03 OUT) ou defaults
    meta = {"fps": 60, "format": "vertical", "title": "DORN", "date": date.today().isoformat()}
    plan_path = p["plan"] if p["plan"].exists() else p["in"] / "plan_de_vol.json"
    if plan_path.exists():
        with open(plan_path, encoding="utf-8") as f:
            plan = json.load(f)
        concept = plan.get("concept_metadata", {})
        meta.update({
            "fps":    plan.get("timing", {}).get("fps", 60),
            "format": concept.get("format", "vertical"),
            "title":  concept.get("title", "DORN"),
        })
        log(f"Plan charge : {plan_path.name}")
    else:
        log("ATTENTION : aucun plan_de_vol.json trouve — utilisation des defaults (vertical, 60fps)")

    fmt   = meta.get("format", "vertical")
    title = meta.get("title", "DORN")
    fps   = meta.get("fps", 60)

    meta["fps"]   = fps
    meta["title"] = title
    meta["date"]  = date.today().isoformat()

    # Nom du fichier de sortie
    out_name  = "youtube_short.mp4" if fmt == "vertical" else "youtube_long.mp4"
    video_out = p["out"] / out_name

    log(f"Format : {fmt.upper()} -> {out_name}")
    log(f"Titre  : {title}")
    log(f"FPS    : {fps}")

    # Detection audio
    audio = has_audio_stream(p["video"])
    log(f"Flux audio : {'oui' if audio else 'non'}")

    # Verification FFmpeg disponible
    r = subprocess.run(["ffmpeg", "-version"], capture_output=True)
    if r.returncode != 0:
        log("ERREUR : ffmpeg introuvable. Sur Colab : sudo apt-get install -y ffmpeg")
        sys.exit(1)

    # FFmpeg camouflage
    p["out"].mkdir(parents=True, exist_ok=True)
    rc = run_ffmpeg(p["video"], video_out, speed, audio, meta)

    if rc != 0:
        log("")
        log("F04B INWIT — FINISHING FAIL — corriger les erreurs FFmpeg ci-dessus")
        sys.exit(1)

    # QA gate
    qa_result = qa_gate(video_out)
    if not qa_result[0]:
        log("F04B — QA FAIL (voir rapport)")

    # Rapport HTML
    generate_rapport_html(str(p["out"]), meta, video_out, speed, qa_result)

    # Touch timestamp
    import time as _time
    ts = _time.time()
    os.utime(video_out, (ts, ts))

    # Resume
    size_mb = video_out.stat().st_size / (1024 * 1024)
    log("")
    log("=" * 62)
    log(f"F04B INWIT — FINISHING {'OK' if qa_result[0] else 'OK (QA warnings)'}")
    log("=" * 62)
    log(f"-> Fichier : {video_out}")
    log(f"-> Taille  : {size_mb:.1f} MB")
    log(f"-> Vitesse : {speed}x")
    log(f"-> Camouflage HELBRECHT applique (wipe metadata + loudnorm + faststart)")
    log(f"-> rapport_f04.html")
    log("-> Telecharger depuis Google Drive pour upload YouTube")


if __name__ == "__main__":
    main()
