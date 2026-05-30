"""
DRN F04B INWIT — FFmpeg Finishing
PENTERACT DORN V3 — VIIe Légion

Rôle : Appliquer setpts si playback_speed != 1.0, produire le fichier
       youtube_*.mp4 final prêt pour upload.

Entrées  : F04_INWIT/IN/video_render.mp4
           F04_INWIT/OUT/speed_validated.json  (produit par F04A)
           F04_INWIT/OUT/plan_de_vol.json       (produit par F04A)

Sorties  : F04_INWIT/OUT/youtube_short.mp4  (si format=vertical)
           F04_INWIT/OUT/youtube_long.mp4   (si format=horizontal)

Logique setpts conditionnel (V3) :
  speed == 1.0  →  stream copy  (-c copy), aucun re-encode, qualité maximale
  speed != 1.0  →  -vf setpts=PTS/{speed}  +  -af atempo={speed} (si audio)
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_DRIVE_BASE = "/content/drive/MyDrive/DRIVE_DORN"

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
# Détection des flux audio via ffprobe
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
# Construction du filtre atempo (gère les valeurs hors 0.5–2.0 par chaînage)
# ─────────────────────────────────────────────────────────────────────────────
def build_atempo(speed: float) -> str:
    if 0.5 <= speed <= 2.0:
        return f"atempo={speed}"
    # Chaînage défensif pour valeurs extrêmes
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
# Pipeline FFmpeg — setpts conditionnel V3
# ─────────────────────────────────────────────────────────────────────────────
def run_ffmpeg(video_in: Path, video_out: Path, speed: float, audio: bool) -> int:
    if speed == 1.0:
        # Stream copy — aucun re-encode, qualité bit-for-bit
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_in),
            "-c", "copy",
            str(video_out),
        ]
        log("Mode : STREAM COPY (playback_speed=1.0 — aucun re-encode)")
    else:
        vf = f"setpts=PTS/{speed}"
        if audio:
            af = build_atempo(speed)
            cmd = [
                "ffmpeg", "-y",
                "-i", str(video_in),
                "-vf", vf,
                "-af", af,
                "-c:v", "libx264", "-crf", "18", "-preset", "fast",
                "-c:a", "aac", "-b:a", "192k",
                str(video_out),
            ]
            log(f"Mode : RE-ENCODE (speed={speed}x | vf={vf} | af={af})")
        else:
            cmd = [
                "ffmpeg", "-y",
                "-i", str(video_in),
                "-vf", vf,
                "-c:v", "libx264", "-crf", "18", "-preset", "fast",
                "-an",
                str(video_out),
            ]
            log(f"Mode : RE-ENCODE video only (speed={speed}x | vf={vf} | pas d'audio)")

    log(f"CMD : {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


# ─────────────────────────────────────────────────────────────────────────────
# ENTRÉE PRINCIPALE
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="DRN F04B INWIT — FFmpeg Finishing")
    parser.add_argument("--drive-base", default=DEFAULT_DRIVE_BASE)
    args = parser.parse_args()

    log("=" * 62)
    log("DRN F04B INWIT — FFmpeg Finishing")
    log("=" * 62)

    p = paths(args.drive_base)

    # ── Vérification des entrées ───────────────────────────────────────────
    checks = [
        (p["video"], "video_render.mp4          (F03 OUT → F04 IN)"),
        (p["speed"], "speed_validated.json      (F04A OUT)"),
        (p["plan"],  "plan_de_vol.json (OUT/)   (F04A OUT)"),
    ]
    for path, label in checks:
        if not path.exists():
            log(f"ERREUR : {label}")
            log(f"         introuvable → {path}")
            sys.exit(1)
        log(f"OK : {label}")

    # ── Charger vitesse validée ────────────────────────────────────────────
    with open(p["speed"], encoding="utf-8") as f:
        sv = json.load(f)
    speed = float(sv["playback_speed"])
    log(f"Vitesse figée : {speed}x")

    # ── Charger plan ──────────────────────────────────────────────────────
    with open(p["plan"], encoding="utf-8") as f:
        plan = json.load(f)
    meta  = plan.get("concept_metadata", {})
    fmt   = meta.get("format", "vertical")
    title = meta.get("title", "DORN")
    fps   = plan.get("timing", {}).get("fps", 60)

    # ── Nom du fichier de sortie ───────────────────────────────────────────
    out_name  = "youtube_short.mp4" if fmt == "vertical" else "youtube_long.mp4"
    video_out = p["out"] / out_name

    log(f"Format : {fmt.upper()} → {out_name}")
    log(f"Titre  : {title}")
    log(f"FPS    : {fps}")

    # ── Détection audio ───────────────────────────────────────────────────
    audio = has_audio_stream(p["video"])
    log(f"Flux audio : {'oui' if audio else 'non'}")

    # ── Vérification FFmpeg disponible ────────────────────────────────────
    r = subprocess.run(["ffmpeg", "-version"], capture_output=True)
    if r.returncode != 0:
        log("ERREUR : ffmpeg introuvable. Sur Colab : sudo apt-get install -y ffmpeg")
        sys.exit(1)

    # ── FFmpeg ────────────────────────────────────────────────────────────
    p["out"].mkdir(parents=True, exist_ok=True)
    rc = run_ffmpeg(p["video"], video_out, speed, audio)

    if rc == 0:
        size_mb = video_out.stat().st_size / (1024 * 1024)
        log("")
        log("=" * 62)
        log("F04B INWIT — FINISHING OK")
        log("=" * 62)
        log(f"→ Fichier : {video_out}")
        log(f"→ Taille  : {size_mb:.1f} MB")
        log(f"→ Vitesse : {speed}x")
        if speed == 1.0:
            log("→ Stream copy — qualité bit-for-bit préservée")
        else:
            log(f"→ Re-encodé — setpts=PTS/{speed}")
        log("→ Télécharger depuis Google Drive pour upload YouTube")
    else:
        log("")
        log("F04B INWIT — FINISHING FAIL — corriger les erreurs FFmpeg ci-dessus")
        sys.exit(1)


if __name__ == "__main__":
    main()
