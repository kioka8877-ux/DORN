"""
drn_f01_polux.py — Frégate F01 POLUX
======================================
PENTERACT DORN V3 — VIIe Légion

Validation plan_de_vol.json V3 + strip EXIF destructif sur tous les PNG.
Stdlib uniquement + Pillow (disponible sur Google Colab sans installation).

Usage (Colab) :
    python drn_f01_polux.py
    python drn_f01_polux.py --drive-base /content/drive/MyDrive/DRIVE_DORN

Entrées  : F01_POLUX/IN/plan_de_vol.json  +  F01_POLUX/IN/images/*.png
Sorties  : F01_POLUX/OUT/plan_de_vol.json +  F01_POLUX/OUT/images/*.png

Exit codes :
    0 = VALIDATION OK — transit F01 → F02 autorisé
    1 = VALIDATION FAIL — corriger les erreurs avant de continuer
"""

import argparse
import json
import os
import re
import shutil
import sys

# ─── Configuration ─────────────────────────────────────────────────────────────

DEFAULT_DRIVE_BASE = "/content/drive/MyDrive/DRIVE_DORN"

VALID_ENGINE_TYPES   = {"time_evolution_comparison", "wave_analysis",
                        "geometric_construction", "single_proof"}
VALID_FORMATS        = {"vertical", "horizontal"}
VALID_REVEAL_STYLES  = {"linear", "ease_in", "ease_out", "ease_in_out", "dramatic"}
VALID_WAVE_TYPES     = {"sine", "square", "sawtooth"}
VALID_GEOMETRY_MODES = {"cartesian", "polar"}
VALID_MOVEMENT_ENERGY = {"calm", "cinematic", "aggressive", "viral_edit"}

# complexity_coefficient attendu par engine_type (tolérance ± 0.05)
EXPECTED_COMPLEXITY = {
    "time_evolution_comparison": 1.0,
    "wave_analysis":             0.6,
    "geometric_construction":    1.8,
    "single_proof":              1.2,
}

HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

# ─── Logging ───────────────────────────────────────────────────────────────────

errors   = []
warnings = []

def ok(msg):   print(f"  [OK]   {msg}")
def fail(msg): print(f"  [FAIL] {msg}"); errors.append(msg)
def warn(msg): print(f"  [WARN] {msg}"); warnings.append(msg)
def info(msg): print(f"  [...]  {msg}")

# ─── Validation helpers ────────────────────────────────────────────────────────

def check_key(obj, key, label, non_empty=True):
    if key not in obj:
        fail(f"{label} — clé manquante : '{key}'")
        return None
    val = obj[key]
    if non_empty and isinstance(val, str) and not val.strip():
        fail(f"{label}.{key} — valeur vide")
        return None
    return val

def check_in(val, valid_set, label):
    if val not in valid_set:
        fail(f"{label} — valeur invalide : '{val}' (attendu : {sorted(valid_set)})")
        return False
    return True


# ─── Validations par niveau ────────────────────────────────────────────────────

def validate_matrix_signature(data):
    info("Niveau 1 — matrix_signature")
    sig = check_key(data, "matrix_signature", "racine")
    if sig and sig != "PENTERACT_DORN_VII_LEGION":
        fail(f"matrix_signature incorrect : '{sig}' (attendu : 'PENTERACT_DORN_VII_LEGION')")
    elif sig:
        ok(f"matrix_signature = {sig}")


def validate_concept_metadata(data):
    info("Niveau 2 — concept_metadata")
    cm = check_key(data, "concept_metadata", "racine", non_empty=False)
    if cm is None:
        return
    for field in ("title", "hook", "thesis"):
        v = check_key(cm, field, "concept_metadata")
        if v:
            ok(f"concept_metadata.{field} = '{v[:60]}{'...' if len(v) > 60 else ''}'")
    engine = check_key(cm, "engine_type", "concept_metadata")
    if engine:
        if check_in(engine, VALID_ENGINE_TYPES, "concept_metadata.engine_type"):
            ok(f"concept_metadata.engine_type = {engine}")
    fmt = check_key(cm, "format", "concept_metadata")
    if fmt:
        if check_in(fmt, VALID_FORMATS, "concept_metadata.format"):
            ok(f"concept_metadata.format = {fmt}")
    fps = check_key(cm, "fps", "concept_metadata", non_empty=False)
    if fps is not None:
        if fps != 60:
            warn(f"concept_metadata.fps = {fps} (standard DORN = 60)")
        else:
            ok("concept_metadata.fps = 60")


def validate_timing(data):
    info("Niveau 3 — timing V3")
    t = check_key(data, "timing", "racine", non_empty=False)
    if t is None:
        return
    engine = data.get("concept_metadata", {}).get("engine_type", "")

    for field in ("fps", "target_duration_seconds", "step_per_frame",
                  "complexity_coefficient", "final_freeze_frames", "playback_speed"):
        v = check_key(t, field, "timing", non_empty=False)
        if v is None:
            continue
        if isinstance(v, (int, float)) and v <= 0:
            fail(f"timing.{field} doit être > 0 (valeur : {v})")
        else:
            ok(f"timing.{field} = {v}")

    xr = check_key(t, "x_range", "timing", non_empty=False)
    if xr:
        start = xr.get("start")
        end   = xr.get("end")
        if start is None or end is None:
            fail("timing.x_range doit avoir 'start' et 'end'")
        elif start >= end:
            fail(f"timing.x_range invalide : start ({start}) >= end ({end})")
        else:
            ok(f"timing.x_range = [{start}, {end}]")

    # Cohérence complexity_coefficient
    if engine in EXPECTED_COMPLEXITY:
        cc = t.get("complexity_coefficient")
        expected = EXPECTED_COMPLEXITY[engine]
        if cc is not None and abs(cc - expected) > 0.05:
            warn(f"timing.complexity_coefficient = {cc} "
                 f"(attendu {expected} pour {engine}) — vérifier intentionnel")
        elif cc is not None:
            ok(f"timing.complexity_coefficient cohérent avec {engine}")

    # Cohérence step_per_frame
    if xr and t.get("target_duration_seconds") and t.get("step_per_frame"):
        xrange_span = xr.get("end", 0) - xr.get("start", 0)
        fps         = t.get("fps", 60)
        dur         = t.get("target_duration_seconds")
        freeze      = t.get("final_freeze_frames", 180)
        expected_spf = xrange_span / (dur * fps - freeze)
        actual_spf   = t.get("step_per_frame")
        if abs(actual_spf - expected_spf) > 0.001:
            warn(f"timing.step_per_frame = {actual_spf} "
                 f"(calcul attendu ≈ {expected_spf:.4f}) — vérifier")
        else:
            ok(f"timing.step_per_frame cohérent ({actual_spf})")


def validate_space_environment(data):
    info("Niveau 4 — space_environment")
    se = check_key(data, "space_environment", "racine", non_empty=False)
    if se is None:
        return
    gm = check_key(se, "geometry_mode", "space_environment")
    if gm:
        if check_in(gm, VALID_GEOMETRY_MODES, "space_environment.geometry_mode"):
            ok(f"space_environment.geometry_mode = {gm}")
    for field in ("x_label", "y_label"):
        v = check_key(se, field, "space_environment")
        if v:
            ok(f"space_environment.{field} = '{v}'")


def validate_reactor_curves(data, png_files):
    info("Niveau 5 — reactor_curves")
    curves = check_key(data, "reactor_curves", "racine", non_empty=False)
    if curves is None:
        return
    if not isinstance(curves, list) or len(curves) == 0:
        fail("reactor_curves doit contenir au moins 1 courbe")
        return
    ok(f"{len(curves)} courbe(s) détectée(s)")
    for i, c in enumerate(curves):
        lbl = f"reactor_curves[{i}]"
        cid = check_key(c, "id", lbl)
        if cid:
            ok(f"{lbl}.id = '{cid}'")
        mi = check_key(c, "math_input", lbl)
        if mi:
            ok(f"{lbl}.math_input = '{mi[:50]}{'...' if len(mi)>50 else ''}'")
        rs = c.get("render_style", {})
        color = rs.get("color_hex", "")
        if not HEX_COLOR_RE.match(color):
            fail(f"{lbl}.render_style.color_hex invalide : '{color}' (format #RRGGBB)")
        else:
            ok(f"{lbl}.render_style.color_hex = {color}")
        aspeed = c.get("animation_speed", {})
        rv = aspeed.get("reveal_style", "")
        if rv and rv not in VALID_REVEAL_STYLES:
            fail(f"{lbl}.animation_speed.reveal_style invalide : '{rv}'")
        elif rv:
            ok(f"{lbl}.animation_speed.reveal_style = {rv}")
        # PNG référencé
        asset = c.get("tracking_target", {}).get("asset_filename", "")
        if asset:
            if asset not in png_files:
                warn(f"{lbl}.tracking_target.asset_filename '{asset}' absent de IN/images/")
            else:
                ok(f"{lbl}.tracking_target.asset_filename = '{asset}' (présent)")


def validate_camera_plan(data):
    info("Niveau 6 — camera_plan")
    cp = check_key(data, "camera_plan", "racine", non_empty=False)
    if cp is None:
        warn("camera_plan absent — sera généré par META_CAMERA avant F02")
        return
    sig = cp.get("camera_signature", "")
    if sig != "DORN_META_CAMERA_V1":
        warn(f"camera_plan.camera_signature = '{sig}' (attendu : 'DORN_META_CAMERA_V1')")
    else:
        ok(f"camera_plan.camera_signature = {sig}")
    gs = cp.get("global_style", {})
    me = gs.get("movement_energy", "")
    if me and me not in VALID_MOVEMENT_ENERGY:
        fail(f"camera_plan.global_style.movement_energy invalide : '{me}'")
    elif me:
        ok(f"camera_plan.global_style.movement_energy = {me}")
    segs = cp.get("camera_segments", [])
    if not segs:
        warn("camera_plan.camera_segments vide")
    else:
        last = segs[-1]
        if last.get("mode") != "final_proof_lock":
            warn("Le dernier segment caméra devrait être 'final_proof_lock'")
        else:
            ok(f"Dernier segment = final_proof_lock ✓")
        ok(f"{len(segs)} segment(s) caméra")


def validate_final_frame(data):
    info("Niveau 7 — final_frame")
    ff = check_key(data, "final_frame", "racine", non_empty=False)
    if ff is None:
        return
    ann = check_key(ff, "annotation", "final_frame")
    if ann:
        ok(f"final_frame.annotation = '{ann[:60]}{'...' if len(ann)>60 else ''}'")
    fdf = ff.get("freeze_duration_frames", 0)
    if fdf <= 0:
        fail(f"final_frame.freeze_duration_frames invalide : {fdf}")
    else:
        ok(f"final_frame.freeze_duration_frames = {fdf}")


def validate_audio(data):
    info("Niveau 8 — audio_synthesizer")
    a = check_key(data, "audio_synthesizer", "racine", non_empty=False)
    if a is None:
        return
    wt = check_key(a, "wave_type", "audio_synthesizer")
    if wt:
        if check_in(wt, VALID_WAVE_TYPES, "audio_synthesizer.wave_type"):
            ok(f"audio_synthesizer.wave_type = {wt}")
    for field in ("base_frequency_hz", "frequency_multiplier"):
        v = check_key(a, field, "audio_synthesizer", non_empty=False)
        if v is not None and v > 0:
            ok(f"audio_synthesizer.{field} = {v}")


# ─── Strip EXIF PNG ─────────────────────────────────────────────────────────────

def strip_exif_png(src_path, dst_path):
    """Recrée le PNG sans aucune métadonnée EXIF/XMP/tEXt."""
    try:
        from PIL import Image
    except ImportError:
        fail("Pillow non disponible — pip install Pillow")
        return False
    try:
        img = Image.open(src_path)
        clean = Image.new(img.mode, img.size)
        clean.putdata(list(img.getdata()))
        clean.save(dst_path, format="PNG", optimize=False)
        src_size = os.path.getsize(src_path)
        dst_size = os.path.getsize(dst_path)
        ok(f"EXIF strip : {os.path.basename(src_path)} "
           f"({src_size:,} → {dst_size:,} bytes)")
        return True
    except Exception as e:
        fail(f"EXIF strip échoué sur {os.path.basename(src_path)} : {e}")
        return False


# ─── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PENTERACT DORN — F01 POLUX — Validation JSON + Strip EXIF PNG"
    )
    parser.add_argument("--drive-base", default=DEFAULT_DRIVE_BASE)
    args = parser.parse_args()
    base = args.drive_base

    in_dir      = os.path.join(base, "F01_POLUX", "IN")
    in_json     = os.path.join(in_dir, "plan_de_vol.json")
    in_img_dir  = os.path.join(in_dir, "images")
    out_dir     = os.path.join(base, "F01_POLUX", "OUT")
    out_json    = os.path.join(out_dir, "plan_de_vol.json")
    out_img_dir = os.path.join(out_dir, "images")

    print()
    print("═══════════════════════════════════════════════════════")
    print("  PENTERACT DORN — F01 POLUX — ORACLE & CURATION")
    print(f"  Drive base : {base}")
    print("═══════════════════════════════════════════════════════")
    print()

    # ── Lecture JSON ────────────────────────────────────────────────────────────
    info(f"Lecture : {in_json}")
    if not os.path.exists(in_json):
        fail(f"plan_de_vol.json absent : {in_json}")
        _exit_report(base)
        return

    try:
        with open(in_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        ok(f"JSON parsé ({os.path.getsize(in_json):,} bytes)")
    except json.JSONDecodeError as e:
        fail(f"JSON invalide : {e}")
        _exit_report(base)
        return

    # ── Inventaire PNG ──────────────────────────────────────────────────────────
    info(f"Inventaire PNG : {in_img_dir}")
    png_files = set()
    if os.path.isdir(in_img_dir):
        png_files = {
            f for f in os.listdir(in_img_dir)
            if f.lower().endswith(".png")
        }
        if png_files:
            ok(f"{len(png_files)} PNG trouvé(s) : {', '.join(sorted(png_files))}")
        else:
            warn("Aucun PNG dans IN/images/ — assets vides")
    else:
        warn(f"Dossier IN/images/ absent : {in_img_dir}")
    print()

    # ── Validations ─────────────────────────────────────────────────────────────
    validate_matrix_signature(data)
    print()
    validate_concept_metadata(data)
    print()
    validate_timing(data)
    print()
    validate_space_environment(data)
    print()
    validate_reactor_curves(data, png_files)
    print()
    validate_camera_plan(data)
    print()
    validate_final_frame(data)
    print()
    validate_audio(data)
    print()

    if errors:
        _exit_report(base)
        return

    # ── Strip EXIF + copie OUT ──────────────────────────────────────────────────
    info("Strip EXIF PNG + copie vers OUT/")
    os.makedirs(out_img_dir, exist_ok=True)

    if png_files:
        for png in sorted(png_files):
            src = os.path.join(in_img_dir, png)
            dst = os.path.join(out_img_dir, png)
            strip_exif_png(src, dst)
    else:
        info("Aucun PNG à traiter")
    print()

    if errors:
        _exit_report(base)
        return

    # ── Copie JSON validé vers OUT ──────────────────────────────────────────────
    os.makedirs(out_dir, exist_ok=True)
    shutil.copy2(in_json, out_json)
    ok(f"plan_de_vol.json copié → {out_json}")
    print()

    _exit_report(base)


def _exit_report(base):
    print("═══════════════════════════════════════════════════════")
    if errors:
        print(f"  F01 POLUX — VALIDATION FAIL — {len(errors)} erreur(s), {len(warnings)} warning(s)")
        print()
        for e in errors:
            print(f"    ✗ {e}")
        print()
        print("  Transit F01 → F02 INTERDIT. Corriger le plan_de_vol.json.")
        print("═══════════════════════════════════════════════════════")
        sys.exit(1)
    else:
        print(f"  F01 POLUX — VALIDATION OK — {len(warnings)} warning(s)")
        if warnings:
            print()
            for w in warnings:
                print(f"    ⚠ {w}")
        print()
        print("  OUT/ prêt. Passer META_CAMERA puis F02 CASTELLAN.")
        print("  Commande de transit :")
        print(f"    python CRS_CUSTOS.py --frigate F01 --mode check-in --drive-base {base}")
        print("═══════════════════════════════════════════════════════")
        sys.exit(0)


if __name__ == "__main__":
    main()
