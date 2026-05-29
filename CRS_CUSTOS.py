"""
CRS_CUSTOS.py — Gardien de Flotte PENTERACT DORN
========================================
Adapté de CRUSADER/CRS_CUSTOS.py — frégates et schémas JSON mis à jour pour PENTERACT DORN.

Valide les fichiers IN/ et OUT/ de chaque frégate avant et après tout transfert.
Stdlib uniquement — aucune dépendance externe.

Usage:
    python CRS_CUSTOS.py --frigate F01 --mode check-out [--drive-base /path]
    python CRS_CUSTOS.py --frigate F02 --mode check-in  [--drive-base /path]

Exit codes:
    0 = VALIDATION OK
    1 = VALIDATION FAIL
"""

import argparse
import json
import os
import sys

# ─── Configuration ────────────────────────────────────────────────────────────

DEFAULT_DRIVE_BASE = "/content/drive/MyDrive/DRIVE_DORN"

# Manifeste de validation par frégate et par mode
# Schéma plan_de_vol.json : {concept_metadata, timing, space_environment, reactor_curves, camera_plan, final_frame, audio_synthesizer}
MANIFEST = {
    "SHARED": {
        "check-out": {
            "dirs": ["SHARED/IN/images"],
        }
    },
    "F01": {
        "check-out": {
            "files": [
                {"path": "F01_POLUX/IN/plan_de_vol.json", "type": "json",
                 "required_keys": ["concept_metadata", "timing", "reactor_curves"]},
            ],
            "dirs": ["F01_POLUX/IN/images"],
        },
        "check-in": {
            "files": [
                {"path": "F01_POLUX/OUT/plan_de_vol.json", "type": "json",
                 "required_keys": ["concept_metadata", "timing", "reactor_curves"]},
            ],
            "dirs": ["F01_POLUX/OUT/images"],
        },
    },
    "F02": {
        "check-out": {
            "files": [
                {"path": "F02_CASTELLAN/IN/plan_de_vol.json", "type": "json",
                 "required_keys": ["concept_metadata", "timing", "reactor_curves"]},
            ],
            "dirs": ["F02_CASTELLAN/IN/images"],
        },
        "check-in": {
            "files": [
                {"path": "F02_CASTELLAN/OUT/plan_de_vol.json", "type": "json",
                 "required_keys": ["concept_metadata", "timing", "reactor_curves",
                                   "validated_by_magos"]},
            ]
        },
    },
    "F03": {
        "check-out": {
            "files": [
                {"path": "F03_SIGISMUND/IN/plan_de_vol.json", "type": "json",
                 "required_keys": ["concept_metadata", "timing", "reactor_curves",
                                   "camera_plan", "validated_by_magos"]},
            ],
            "dirs": ["F03_SIGISMUND/IN/images"],
        },
        "check-in": {
            "files": [
                {"path": "F03_SIGISMUND/OUT/video_render.mp4", "type": "file",
                 "min_size": 100000},
            ]
        },
    },
    "F04": {
        "check-out": {
            "files": [
                {"path": "F04_INWIT/IN/video_render.mp4", "type": "file",
                 "min_size": 100000},
                {"path": "F04_INWIT/IN/plan_de_vol.json", "type": "json",
                 "required_keys": ["concept_metadata", "timing"]},
            ]
        },
        "check-in": {
            "one_of": [
                {"path": "F04_INWIT/OUT/youtube_short.mp4", "type": "file",
                 "min_size": 100000},
                {"path": "F04_INWIT/OUT/youtube_long.mp4", "type": "file",
                 "min_size": 100000},
            ]
        },
    },
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def log_ok(msg):
    print(f"  [OK]   {msg}")

def log_fail(msg):
    print(f"  [FAIL] {msg}")

def log_info(msg):
    print(f"  [...]  {msg}")

def validate_file(full_path, spec):
    if not os.path.exists(full_path):
        log_fail(f"Fichier absent : {full_path}")
        return False
    if spec.get("type") == "json":
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            log_fail(f"JSON invalide ({full_path}) : {e}")
            return False
        for key in spec.get("required_keys", []):
            if key not in data:
                log_fail(f"Clé manquante \'{key}\' dans {full_path}")
                return False
        log_ok(f"{full_path}")
        return True
    if spec.get("type") == "file":
        size = os.path.getsize(full_path)
        min_size = spec.get("min_size", 0)
        if size < min_size:
            log_fail(f"Fichier trop petit ({size} bytes < {min_size}) : {full_path}")
            return False
        log_ok(f"{full_path} ({size:,} bytes)")
        return True
    log_ok(full_path)
    return True

def validate_one_of(candidates, base):
    for spec in candidates:
        full_path = os.path.join(base, spec["path"])
        if not os.path.exists(full_path):
            continue
        size = os.path.getsize(full_path)
        if spec.get("type") == "file" and size < spec.get("min_size", 0):
            continue
        log_ok(f"Vidéo finale : {os.path.basename(full_path)} ({size:,} bytes)")
        return True
    names = " | ".join(os.path.basename(s["path"]) for s in candidates)
    log_fail(f"Aucun fichier de sortie valide trouvé parmi : {names}")
    return False

def validate_dir(full_path):
    if not os.path.isdir(full_path):
        log_fail(f"Dossier absent : {full_path}")
        return False
    contents = os.listdir(full_path)
    if not contents:
        log_fail(f"Dossier vide : {full_path}")
        return False
    log_ok(f"{full_path}/ ({len(contents)} fichier(s))")
    return True

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="CRS_CUSTOS — Gardien de Flotte PENTERACT DORN")
    parser.add_argument("--frigate",    required=True, choices=["SHARED", "F01", "F02", "F03", "F04"])
    parser.add_argument("--mode",       required=True, choices=["check-out", "check-in"])
    parser.add_argument("--drive-base", default=DEFAULT_DRIVE_BASE)
    args = parser.parse_args()

    base    = args.drive_base
    frigate = args.frigate
    mode    = args.mode

    print()
    print(f"═══════════════════════════════════════════════")
    print(f"  CRS_CUSTOS PENTERACT DORN — {frigate} — {mode.upper()}")
    print(f"  Drive base : {base}")
    print(f"═══════════════════════════════════════════════")

    spec = MANIFEST.get(frigate, {}).get(mode)
    if spec is None:
        print(f"  [INFO] Aucune validation définie pour {frigate} / {mode}. Passage autorisé.")
        sys.exit(0)

    errors = 0

    for file_spec in spec.get("files", []):
        full = os.path.join(base, file_spec["path"])
        log_info(f"Vérification : {file_spec['path']}")
        if not validate_file(full, file_spec):
            errors += 1

    for dir_path in spec.get("dirs", []):
        full = os.path.join(base, dir_path)
        log_info(f"Vérification dossier : {dir_path}")
        if not validate_dir(full):
            errors += 1

    one_of = spec.get("one_of", [])
    if one_of:
        names = " | ".join(os.path.basename(s["path"]) for s in one_of)
        log_info(f"Vérification (un parmi) : {names}")
        if not validate_one_of(one_of, base):
            errors += 1

    print()
    if errors == 0:
        print(f"  VALIDATION OK — {frigate} {mode} : Aucune erreur.")
        print(f"═══════════════════════════════════════════════")
        sys.exit(0)
    else:
        print(f"  VALIDATION FAIL — {errors} erreur(s) détectée(s). Transit interdit.")
        print(f"═══════════════════════════════════════════════")
        sys.exit(1)


if __name__ == "__main__":
    main()
