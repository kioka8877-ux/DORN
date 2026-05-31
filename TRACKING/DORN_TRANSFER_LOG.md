# DORN — TRANSFER LOG
## Registre des Transferts Inter-Frégates

---

## Procédure Standard de Transit

1. `python CRS_CUSTOS.py --frigate <SOURCE> --mode check-out --drive-base /content/drive/MyDrive/DRIVE_DORN`
2. Copier manuellement les fichiers (source OUT/ → destination IN/)
3. `python CRS_CUSTOS.py --frigate <DEST> --mode check-in --drive-base /content/drive/MyDrive/DRIVE_DORN`
4. Logger le transfert dans ce fichier

**Règle absolue : Aucun transfert sans validation CUSTOS aux deux extrémités.**

---

## Schémas JSON — Contrats de Données

### plan_de_vol.json — VERSION F01 OUT (produit par META_POLUX + validé par F01)

```json
{
  "matrix_signature": "PENTERACT_DORN_VII_LEGION",
  "concept_metadata": {
    "title": "string — titre viral",
    "hook": "string — accroche 1 phrase",
    "thesis": "string — la thèse mathématique",
    "engine_type": "time_evolution_comparison | geometric_construction | wave_analysis | single_proof",
    "format": "vertical | horizontal",
    "fps": 60
  },
  "timing": {
    "fps": 60,
    "target_duration_seconds": 30,
    "x_range": { "start": 0, "end": 20 },
    "step_per_frame": 0.05,
    "complexity_coefficient": 1.0,
    "final_freeze_frames": 180,
    "playback_speed": 1.0
  },
  "space_environment": {
    "geometry_mode": "cartesian | polar",
    "x_label": "string",
    "y_label": "string",
    "background_asset": "filename.png (optionnel)"
  },
  "reactor_curves": [
    {
      "id": "string",
      "math_input": "string — expression math.js",
      "render_style": {
        "color_hex": "#XXXXXX",
        "glow_radius_px": 20,
        "line_width_px": 6
      },
      "animation_speed": {
        "reveal_style": "linear | ease_in | ease_out | dramatic",
        "pace_factor": 1.0
      },
      "tracking_target": {
        "asset_filename": "face.png",
        "scale_factor": 1.2,
        "physics": {
          "auto_rotate_slope": true,
          "inertia_smooth": 0.1
        }
      }
    }
  ],
  "final_frame": {
    "annotation": "string — texte de conclusion mathématique",
    "freeze_duration_frames": 90
  },
  "audio_synthesizer": {
    "wave_type": "sine | square | sawtooth",
    "base_frequency_hz": 220,
    "frequency_multiplier": 12.0
  }
}
```

### plan_de_vol.json — VERSION F02 OUT (figé par CASTELLAN)

Même schéma + ajout du bloc `camera_plan` (injecté par META_CAMERA) et :

```json
{
  "...": "...",
  "camera_plan": {
    "camera_signature": "DORN_META_CAMERA_V1",
    "global_style": {
      "movement_energy": "calm | cinematic | aggressive | viral_edit",
      "default_easing": "easeInOutCubic",
      "shake_intensity": 0.08
    },
    "camera_segments": [
      {
        "start_frame": 0,
        "end_frame": 180,
        "mode": "follow_asset | static | wide_reveal | push_in | final_proof_lock",
        "target_curve_id": "string",
        "zoom": 1.15,
        "x_offset": 0,
        "y_offset": -40,
        "shake": 0.03
      }
    ]
  },
  "validated_by_magos": true
}
```

**`validated_by_magos: true` est positionné par F02 au moment de la sauvegarde — jamais manuellement.**

---

## Logique de Durée Dynamique (V3)

```
reveal_frames = (x_range.end - x_range.start) / step_per_frame
total_frames  = reveal_frames × complexity_coefficient + final_freeze_frames

// Calcul inverse (META_POLUX) :
step_per_frame = x_range / (target_duration_seconds × fps − final_freeze_frames)
```

| engine_type | complexity_coefficient |
|---|---|
| time_evolution_comparison | 1.0 |
| wave_analysis | 0.6 |
| geometric_construction | 1.8 |
| single_proof | 1.2 |

---

## Matrice des Routes Légales

| Source | Destination | Fichiers transférés |
|--------|-------------|---------------------|
| SHARED | F01 IN | images/*.png |
| META_POLUX (Gemini chat) | F01 IN | plan_de_vol.json |
| F01 OUT | F02 IN | plan_de_vol.json + images/*.png (EXIF propres) |
| META_CAMERA (Gemini chat) | F02 IN | injection camera_plan dans plan_de_vol.json |
| F02 OUT | F03 IN | plan_de_vol.json (figé, validated_by_magos) + images/*.png |
| F03 OUT | F04 IN | video_render.mp4 |
| F02 OUT | F04 IN | plan_de_vol.json (pour format + titre + playback_speed) |

---

## Registre des Transferts

| # | Date | Campagne | Source | Destination | Fichiers | CUSTOS Out | CUSTOS In | Statut |
|---|------|----------|--------|-------------|----------|------------|-----------|--------|
| 1 | 2026-05-31 | CAMP_02 | F01 POLUX OUT | F02 CASTELLAN IN | plan_de_vol.json + images/*.png | — | ✓ CHECK-IN OK | TRANSIT AUTORISÉ |

---

*Tout transfert non loggé ici est considéré non validé.*
