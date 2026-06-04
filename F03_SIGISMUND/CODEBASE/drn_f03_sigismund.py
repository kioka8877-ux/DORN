"""
DRN F03 SIGISMUND — Remotion SVG Neon Renderer
PENTERACT DORN V3 — VIIe Légion

Modes :
  --mode direct   → rendu direct Remotion (1 worker, Colab GPU-less)
  --mode modal    → rendu chunke Modal (3 workers paralleles, herite CRUSADER)
  --mode github   → rendu distribue GitHub Actions (10 workers, image Docker ghcr.io)

Prerequis communs :
  - plan_de_vol.json dans F03_SIGISMUND/IN/ avec validated_by_magos: true
  - images PNG dans F03_SIGISMUND/IN/ (si tracking_target utilise)

Prerequis mode github :
  - --github-token  : PAT avec permissions repo + packages:write
  - --repo          : ex. kioka8877-ux/DORN
  - Secret GH_TOKEN configure dans Settings → Secrets → Actions du repo
"""

import argparse
import base64
import json
import math
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_DRIVE_BASE = "/content/drive/MyDrive/DRIVE_DORN"
FRIGATE            = "F03_SIGISMUND"

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def log(msg: str):
    print(f"[DRN-F03] {msg}", flush=True)


def paths(drive_base: str) -> dict:
    base = Path(drive_base) / FRIGATE
    return {
        "in":       base / "IN",
        "out":      base / "OUT",
        "codebase": base / "CODEBASE",
        "plan":     base / "IN" / "plan_de_vol.json",
        "video":    base / "OUT" / "video_render.mp4",
    }


def load_plan(plan_path: Path) -> dict:
    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)
    if not plan.get("validated_by_magos"):
        log("ERREUR : plan_de_vol.json non validé par CASTELLAN (validated_by_magos manquant)")
        sys.exit(1)
    log(f"Plan chargé : « {plan['concept_metadata']['title']} »")
    return plan


def compute_total_frames(plan: dict) -> int:
    t       = plan["timing"]
    reveal  = (t["x_range"]["end"] - t["x_range"]["start"]) / t["step_per_frame"]
    coeff   = t.get("complexity_coefficient", 1.0)
    freeze  = t.get("final_freeze_frames", 180)
    total   = int(reveal * coeff) + freeze
    fps     = t.get("fps", 60)
    log(f"Frames : {total}  ({total / fps:.1f}s @ {fps}fps)")
    return total


def compute_y_range(plan: dict) -> tuple[float, float]:
    """Pre-calcule le range Y pour le coordinate mapping (utilisé dans --props)."""
    import math as _m
    t       = plan["timing"]
    geo     = plan["space_environment"]["geometry_mode"]
    curves  = plan["reactor_curves"]
    x_start = t["x_range"]["start"]
    x_end   = t["x_range"]["end"]
    samples = 300
    dx      = (x_end - x_start) / samples
    y_min, y_max = float("inf"), float("-inf")

    # Conversion math.js → Python (subset sécurisé)
    import re as _re
    def py_expr(expr: str) -> str:
        result = (
            expr
            .replace("^", "**")
            .replace("sin(",  "_m.sin(")
            .replace("cos(",  "_m.cos(")
            .replace("tan(",  "_m.tan(")
            .replace("exp(",  "_m.exp(")
            .replace("sqrt(", "_m.sqrt(")
            .replace("log(",  "_m.log(")
            .replace("abs(",  "abs(")
            .replace("pi",    str(_m.pi))
        )
        return _re.sub(r'\be\b', str(_m.e), result)

    safe = {"__builtins__": {}, "_m": _m}
    for curve in curves:
        expr = py_expr(curve["math_input"])
        for i in range(samples + 1):
            x = x_start + i * dx
            try:
                y = eval(expr, {**safe, "x": x, "t": x})
                if _m.isfinite(y):
                    if y < y_min: y_min = y
                    if y > y_max: y_max = y
            except Exception:
                pass

    if not _m.isfinite(y_min):
        y_min, y_max = -2.0, 2.0

    padding = abs(y_max - y_min) * 0.12
    return y_min - padding, y_max + padding


def setup_public_assets(p: dict):
    """Copie les PNG de IN/ vers CODEBASE/public/IN/ pour Remotion."""
    public_in = p["codebase"] / "public" / "IN"
    public_in.mkdir(parents=True, exist_ok=True)
    count = 0
    for png in p["in"].glob("*.png"):
        shutil.copy2(png, public_in / png.name)
        count += 1
    if count:
        log(f"{count} PNG copiés → {public_in}")


def ensure_npm_install(codebase: Path):
    if not (codebase / "node_modules").exists():
        log("npm install …")
        subprocess.run(["npm", "install", "--prefer-offline"], cwd=codebase, check=True)
    else:
        log("node_modules déjà présent — skip npm install")


# ─────────────────────────────────────────────────────────────────────────────
# MODE DIRECT (1 worker Colab)
# ─────────────────────────────────────────────────────────────────────────────
def render_direct(p: dict, plan: dict, total_frames: int, y_min: float, y_max: float):
    log("Mode : rendu direct (1 worker)")
    p["out"].mkdir(parents=True, exist_ok=True)
    setup_public_assets(p)
    ensure_npm_install(p["codebase"])

    props = json.dumps({
        "planDeVol": plan,
        "computed":  {"yMin": y_min, "yMax": y_max, "totalFrames": total_frames},
    })

    cmd = [
        "npx", "remotion", "render", "Main",
        str(p["video"]),
        "--gl",          "swangle",
        "--concurrency", "1",
        "--props",       props,
    ]
    log("Lancement Remotion render …")
    result = subprocess.run(cmd, cwd=p["codebase"])
    if result.returncode != 0:
        log("ERREUR : rendu Remotion échoué")
        sys.exit(1)
    log(f"Rendu terminé  →  {p['video']}")


# ─────────────────────────────────────────────────────────────────────────────
# MODE MODAL (3 workers — hérité CRUSADER F03)
# ─────────────────────────────────────────────────────────────────────────────
MODAL_WORKER_TEMPLATE = '''\
import modal, json, os, subprocess, sys, tarfile, tempfile, base64

app       = modal.App("{app_name}")
N_WORKERS = 3

remotion_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "nodejs", "npm", "chromium", "libgbm1", "libasound2",
        "libatk1.0-0", "libcups2", "libdbus-1-3", "libgdk-pixbuf2.0-0",
        "libnspr4", "libnss3", "libx11-xcb1", "libxcomposite1",
        "libxdamage1", "libxrandr2", "xdg-utils", "libxshmfence1",
    )
    .run_commands("npm install -g npm@latest")
)


@app.function(image=remotion_image, timeout=3600, memory=8192, cpu=4)
def render_chunk(info: dict) -> dict:
    work  = tempfile.mkdtemp()
    tar_p = os.path.join(work, "cb.tar.gz")

    with open(tar_p, "wb") as f:
        f.write(base64.b64decode(info["codebase_b64"]))
    with tarfile.open(tar_p, "r:gz") as tar:
        tar.extractall(work)

    cb = os.path.join(work, "CODEBASE")

    # Assets PNG
    pub_in = os.path.join(cb, "public", "IN")
    os.makedirs(pub_in, exist_ok=True)
    for fname, b64 in (info.get("assets_b64") or {{}}).items():
        with open(os.path.join(pub_in, fname), "wb") as f:
            f.write(base64.b64decode(b64))

    subprocess.run(["npm", "install", "--prefer-offline"], cwd=cb, check=True)

    out_dir = os.path.join(cb, "OUT_CHUNKS")
    os.makedirs(out_dir, exist_ok=True)
    chunk_out = os.path.join(out_dir, f"chunk_{{info['chunk_id']}}.mp4")

    cmd = [
        "npx", "remotion", "render", "Main", chunk_out,
        "--gl", "swangle",
        "--frames",      f"{{info['start_frame']}}-{{info['end_frame']}}",
        "--concurrency", "1",
        "--props",       json.dumps(info["props"]),
    ]
    result = subprocess.run(cmd, cwd=cb, capture_output=True, text=True)
    if result.returncode != 0:
        return {{"success": False, "error": result.stderr[-2000:], "chunk_id": info["chunk_id"]}}

    with open(chunk_out, "rb") as f:
        return {{"success": True, "chunk_id": info["chunk_id"],
                "video_b64": base64.b64encode(f.read()).decode()}}


@app.local_entrypoint()
def main():
    import pathlib, json as _json
    info_path = pathlib.Path("{info_json_path}")
    chunks    = _json.loads(info_path.read_text())
    results   = list(render_chunk.map(chunks))

    out_dir   = pathlib.Path("{output_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    chunk_paths = []
    for r in sorted(results, key=lambda x: x["chunk_id"]):
        if not r["success"]:
            print(f"[ERREUR chunk {{r['chunk_id']}}] {{r['error']}}")
            sys.exit(1)
        p = out_dir / f"chunk_{{r['chunk_id']}}.mp4"
        p.write_bytes(base64.b64decode(r["video_b64"]))
        chunk_paths.append(str(p))

    # Concat FFmpeg
    list_file = out_dir / "chunks.txt"
    list_file.write_text("\\n".join(f"file \\'{{c}}\\'" for c in chunk_paths))
    final = "{final_video}"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file), "-c", "copy", final,
    ], check=True)
    print(f"[DRN-F03] Rendu Modal terminé  →  {{final}}")
'''


def render_modal(p: dict, plan: dict, total_frames: int, y_min: float, y_max: float):
    log("Mode : rendu Modal (3 workers)")
    try:
        import modal  # noqa
    except ImportError:
        log("Installation de Modal …")
        subprocess.run([sys.executable, "-m", "pip", "install", "modal", "-q"], check=True)

    tmp = Path(tempfile.mkdtemp())

    # Tar du codebase
    log("Compression du codebase …")
    tar_path = tmp / "codebase.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(p["codebase"], arcname="CODEBASE")
    codebase_b64 = base64.b64encode(tar_path.read_bytes()).decode()

    # Assets PNG
    assets_b64 = {}
    for png in p["in"].glob("*.png"):
        assets_b64[png.name] = base64.b64encode(png.read_bytes()).decode()

    N_WORKERS = 3
    chunk_size = total_frames // N_WORKERS
    props_base = {
        "planDeVol": plan,
        "computed":  {"yMin": y_min, "yMax": y_max, "totalFrames": total_frames},
    }

    chunks = []
    for i in range(N_WORKERS):
        start = i * chunk_size
        end   = total_frames - 1 if i == N_WORKERS - 1 else (i + 1) * chunk_size - 1
        chunks.append({
            "chunk_id":    i,
            "start_frame": start,
            "end_frame":   end,
            "codebase_b64": codebase_b64,
            "assets_b64":  assets_b64,
            "props":       props_base,
        })

    info_json = tmp / "chunks_info.json"
    info_json.write_text(json.dumps(chunks))

    p["out"].mkdir(parents=True, exist_ok=True)
    worker_code = MODAL_WORKER_TEMPLATE.format(
        app_name      = "drn-f03-sigismund",
        info_json_path = str(info_json),
        output_dir    = str(tmp / "chunks_out"),
        final_video   = str(p["video"]),
    )
    worker_path = tmp / "modal_worker.py"
    worker_path.write_text(worker_code)

    log(f"Worker Modal écrit → {worker_path}")
    log("Lancement : modal run modal_worker.py")
    result = subprocess.run(
        ["modal", "run", str(worker_path)],
        cwd=str(tmp),
    )
    if result.returncode != 0:
        log("ERREUR : Modal render échoué")
        sys.exit(1)
    log(f"Rendu Modal terminé  →  {p['video']}")


# ─────────────────────────────────────────────────────────────────────────────
# MODE GITHUB (10 workers GitHub Actions)
# ─────────────────────────────────────────────────────────────────────────────
def render_github(p: dict, plan: dict, total_frames: int, github_token: str, repo: str):
    log("Mode : rendu GitHub Actions (10 workers)")
    import time as _time
    from drn_f03_gh_trigger import (
        upload_assets_to_release,
        ensure_docker_image,
        trigger_workflow,
        poll_run_status,
        download_final_artifact,
    )

    run_id = f"drn-{int(_time.time())}"
    fps    = plan.get("timing", {}).get("fps", 60)
    log(f"Run ID : {run_id} | fps={fps} | total_frames={total_frames}")

    # Etape 1 : Upload assets vers GitHub Release temporaire
    log("--- Etape 1/5 : Upload assets ---")
    upload_assets_to_release(str(p["in"]), run_id, github_token, repo)

    # Etape 2 : Verifier / builder l'image Docker
    log("--- Etape 2/5 : Image Docker ---")
    ok = ensure_docker_image(github_token, repo)
    if not ok:
        log("ERREUR : image Docker indisponible — aborter")
        sys.exit(1)

    # Etape 3 : Declencher le workflow
    log("--- Etape 3/5 : Declenchement workflow ---")
    gh_run_id = trigger_workflow(run_id, fps, "Main", total_frames, github_token, repo)

    # Etape 4 : Polling jusqu'a completion
    log("--- Etape 4/5 : Polling ---")
    poll_run_status(gh_run_id, github_token, repo)

    # Etape 5 : Telecharger l'artifact final
    log("--- Etape 5/5 : Telechargement ---")
    p["out"].mkdir(parents=True, exist_ok=True)
    out_path = download_final_artifact(gh_run_id, run_id, github_token, repo, str(p["out"]))
    log(f"Rendu GitHub termine  →  {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRÉE PRINCIPALE
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="DRN F03 SIGISMUND — Remotion Renderer")
    parser.add_argument(
        "--mode", choices=["direct", "modal", "github"], default="direct",
        help="direct = 1 worker Colab | modal = 3 workers Modal | github = 10 workers GitHub Actions",
    )
    parser.add_argument(
        "--drive-base", default=DEFAULT_DRIVE_BASE,
        help="Chemin de base Google Drive (defaut : DRIVE_DORN)",
    )
    parser.add_argument(
        "--github-token", default=None,
        help="PAT GitHub (requis pour --mode github)",
    )
    parser.add_argument(
        "--repo", default="kioka8877-ux/DORN",
        help="Repo GitHub owner/name (defaut : kioka8877-ux/DORN)",
    )
    args = parser.parse_args()

    log("=" * 62)
    log("DRN F03 SIGISMUND — Demarrage")
    log("=" * 62)

    p            = paths(args.drive_base)
    plan         = load_plan(p["plan"])
    total_frames = compute_total_frames(plan)
    y_min, y_max = compute_y_range(plan)
    log(f"Range Y : [{y_min:.3f}, {y_max:.3f}]")

    if args.mode == "modal":
        render_modal(p, plan, total_frames, y_min, y_max)
    elif args.mode == "github":
        if not args.github_token:
            log("ERREUR : --github-token requis pour --mode github")
            sys.exit(1)
        render_github(p, plan, total_frames, args.github_token, args.repo)
    else:
        render_direct(p, plan, total_frames, y_min, y_max)

    log("F03 SIGISMUND — Mission accomplie.")


if __name__ == "__main__":
    main()
