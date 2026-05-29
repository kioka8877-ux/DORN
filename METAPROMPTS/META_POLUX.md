# META_POLUX — Metaprompt Gemini
## Oracle & Curation — PENTERACT DORN F01
### STATUT : SCELLÉ — V3 — 2026-05-29

---

## Rôle

Ce metaprompt est la **porte d'entrée absolue** du pipeline PENTERACT DORN.
Il transforme un concept pop-culture en `plan_de_vol.json` V3 complet et exploitable.

**S'exécute en chat manuel Gemini — aucun appel API dans le code.**

---

## Instructions d'utilisation

1. Ouvre Gemini (chat.google.com ou Gemini Advanced)
2. Copie-colle le bloc **PROMPT GEMINI** ci-dessous en entier
3. Remplace les 4 balises `[INPUT_X]` par tes réponses réelles
4. Envoie — Gemini génère le `plan_de_vol.json` complet

---

## Les 4 Inputs Opérateur

| # | Balise | Question | Exemple |
|---|--------|----------|---------|
| 1 | `[INPUT_1]` | Sujet + thèse en 1 phrase | `Messi est meilleur que CR7 grâce à son centre de gravité bas` |
| 2 | `[INPUT_2]` | Réponse mathématique souhaitée | `Montrer que stabilité = f(hauteur centre de gravité)` |
| 3 | `[INPUT_3]` | Assets PNG disponibles (noms de fichiers) | `messi_head.png, cr7_head.png` |
| 4 | `[INPUT_4]` | Durée cible de la vidéo | `30 secondes` / `45 secondes` / `1 minute` |

---

## PROMPT GEMINI (copier-coller intégral)

```
Tu es l'Oracle POLUX du pipeline PENTERACT DORN — un système de visualisation mathématique
Pop-Science Culture pour YouTube Shorts / TikTok.

Ta mission : transformer le concept ci-dessous en un plan_de_vol.json V3 complet et prêt
à entrer dans le pipeline de production.

=== INPUTS OPÉRATEUR ===

INPUT 1 — Sujet + thèse :
[INPUT_1]

INPUT 2 — Réponse mathématique souhaitée :
[INPUT_2]

INPUT 3 — Assets PNG disponibles :
[INPUT_3]

INPUT 4 — Durée cible :
[INPUT_4]

=== RÈGLES DE GÉNÉRATION ===

ÉTAPE 1 — Choix du engine_type
Choisis parmi ces 4 types selon le sujet :
- time_evolution_comparison  → comparaison évolutive (Messi vs CR7, Kobe vs Jordan)
- geometric_construction     → construction géométrique (spirale, nombre d'or)
- wave_analysis              → analyse d'ondes (voix, fréquences, harmoniques)
- single_proof               → preuve unique décisive (croissance exponentielle)

ÉTAPE 2 — Calcul du timing dynamique
Paramètres à calculer :
- fps = 60 (fixe)
- final_freeze_frames = 180 (fixe)
- x_range = déterminé par la nature mathématique du sujet (ex: [0, 20] pour sigmoid)
- complexity_coefficient selon le engine_type :
    time_evolution_comparison → 1.0
    wave_analysis             → 0.6
    geometric_construction    → 1.8
    single_proof              → 1.2
- target_duration_seconds = extrait de INPUT 4 (converti en secondes entiers)
- step_per_frame = (x_range.end - x_range.start) / (target_duration_seconds * fps - final_freeze_frames)
  Arrondir à 4 décimales.

ÉTAPE 3 — Génération des courbes reactor_curves
- Minimum 2 courbes si comparaison, sinon 1 courbe principale
- math_input : expression compatible math.js (ex: "1 / (1 + exp(-(x - 5)))")
- Couleurs neon distinctes par courbe (ex: #00FFD1, #FF3366, #FFD700)
- glow_radius_px = 20, line_width_px = 6
- reveal_style adapté :
    time_evolution_comparison → ease_in_out
    wave_analysis             → linear
    geometric_construction    → dramatic
    single_proof              → ease_in
- pace_factor : 1.0 par défaut, ajustable si une courbe doit révéler plus vite

ÉTAPE 4 — Génération du hook viral et des métadonnées
- title : accroche courte, choc émotionnel, 6-10 mots max
- hook : 1 phrase d'accroche narrative (tension + révélation mathématique)
- thesis : la thèse mathématique en 1 phrase technique

ÉTAPE 5 — Attribution des assets PNG
Pour chaque PNG listé en INPUT 3, associe-le à la courbe la plus pertinente.
scale_factor = 1.2, auto_rotate_slope = true, inertia_smooth = 0.1

ÉTAPE 6 — Génération de la final_frame
- annotation : texte de conclusion mathématique court (15 mots max)
- freeze_duration_frames = 90 (fixe)

ÉTAPE 7 — Audio
- wave_type = "sine"
- base_frequency_hz = 220
- frequency_multiplier = 12.0

=== FORMAT DE SORTIE OBLIGATOIRE ===

Réponds UNIQUEMENT avec le JSON ci-dessous, sans texte avant ni après.
Remplis TOUS les champs. Ne laisse aucun champ vide.

{
  "matrix_signature": "PENTERACT_DORN_VII_LEGION",
  "concept_metadata": {
    "title": "",
    "hook": "",
    "thesis": "",
    "engine_type": "",
    "format": "vertical",
    "fps": 60
  },
  "timing": {
    "fps": 60,
    "target_duration_seconds": 0,
    "x_range": { "start": 0, "end": 0 },
    "step_per_frame": 0.0,
    "complexity_coefficient": 0.0,
    "final_freeze_frames": 180,
    "playback_speed": 1.0
  },
  "space_environment": {
    "geometry_mode": "",
    "x_label": "",
    "y_label": "",
    "background_asset": ""
  },
  "reactor_curves": [
    {
      "id": "",
      "math_input": "",
      "render_style": {
        "color_hex": "",
        "glow_radius_px": 20,
        "line_width_px": 6
      },
      "animation_speed": {
        "reveal_style": "",
        "pace_factor": 1.0
      },
      "tracking_target": {
        "asset_filename": "",
        "scale_factor": 1.2,
        "physics": {
          "auto_rotate_slope": true,
          "inertia_smooth": 0.1
        }
      }
    }
  ],
  "camera_plan": {
    "camera_signature": "DORN_META_CAMERA_V1",
    "global_style": {
      "movement_energy": "",
      "default_easing": "easeInOutCubic",
      "shake_intensity": 0.08
    },
    "camera_segments": [
      {
        "start_frame": 0,
        "end_frame": 0,
        "mode": "",
        "target_curve_id": "",
        "zoom": 1.15,
        "x_offset": 0,
        "y_offset": -40,
        "shake": 0.03
      }
    ]
  },
  "final_frame": {
    "annotation": "",
    "freeze_duration_frames": 90
  },
  "audio_synthesizer": {
    "wave_type": "sine",
    "base_frequency_hz": 220,
    "frequency_multiplier": 12.0
  }
}
```

---

## Exemple de Sortie Attendue (Messi vs CR7 — 30 secondes)

```json
{
  "matrix_signature": "PENTERACT_DORN_VII_LEGION",
  "concept_metadata": {
    "title": "La Physique Prouve Que Messi Est Imbattable",
    "hook": "La science a tranché le débat le plus chaud du foot mondial.",
    "thesis": "La stabilité biomécanique est une fonction inverse de la hauteur du centre de gravité.",
    "engine_type": "time_evolution_comparison",
    "format": "vertical",
    "fps": 60
  },
  "timing": {
    "fps": 60,
    "target_duration_seconds": 30,
    "x_range": { "start": 0, "end": 10 },
    "step_per_frame": 0.0556,
    "complexity_coefficient": 1.0,
    "final_freeze_frames": 180,
    "playback_speed": 1.0
  },
  "space_environment": {
    "geometry_mode": "cartesian",
    "x_label": "Hauteur centre de gravité (normalisée)",
    "y_label": "Indice de stabilité",
    "background_asset": ""
  },
  "reactor_curves": [
    {
      "id": "messi",
      "math_input": "1 / (1 + exp(x - 3))",
      "render_style": {
        "color_hex": "#00FFD1",
        "glow_radius_px": 20,
        "line_width_px": 6
      },
      "animation_speed": {
        "reveal_style": "ease_in_out",
        "pace_factor": 1.0
      },
      "tracking_target": {
        "asset_filename": "messi_head.png",
        "scale_factor": 1.2,
        "physics": {
          "auto_rotate_slope": true,
          "inertia_smooth": 0.1
        }
      }
    },
    {
      "id": "cr7",
      "math_input": "1 / (1 + exp(x - 6))",
      "render_style": {
        "color_hex": "#FF3366",
        "glow_radius_px": 20,
        "line_width_px": 6
      },
      "animation_speed": {
        "reveal_style": "ease_in_out",
        "pace_factor": 1.0
      },
      "tracking_target": {
        "asset_filename": "cr7_head.png",
        "scale_factor": 1.2,
        "physics": {
          "auto_rotate_slope": true,
          "inertia_smooth": 0.1
        }
      }
    }
  ],
  "camera_plan": {
    "camera_signature": "DORN_META_CAMERA_V1",
    "global_style": {
      "movement_energy": "cinematic",
      "default_easing": "easeInOutCubic",
      "shake_intensity": 0.08
    },
    "camera_segments": [
      {
        "start_frame": 0,
        "end_frame": 1620,
        "mode": "follow_asset",
        "target_curve_id": "messi",
        "zoom": 1.15,
        "x_offset": 0,
        "y_offset": -40,
        "shake": 0.03
      },
      {
        "start_frame": 1620,
        "end_frame": 1800,
        "mode": "final_proof_lock",
        "target_curve_id": "",
        "zoom": 1.0,
        "x_offset": 0,
        "y_offset": 0,
        "shake": 0.0
      }
    ]
  },
  "final_frame": {
    "annotation": "Messi : Delta stabilité +23% — La physique a parlé.",
    "freeze_duration_frames": 90
  },
  "audio_synthesizer": {
    "wave_type": "sine",
    "base_frequency_hz": 220,
    "frequency_multiplier": 12.0
  }
}
```

---

## Vérification avant de passer à F01

Avant de déposer le JSON dans `F01_POLUX/IN/`, vérifie manuellement :

- [ ] `matrix_signature` = `"PENTERACT_DORN_VII_LEGION"`
- [ ] `step_per_frame` calculé (pas zéro)
- [ ] `complexity_coefficient` correspond au `engine_type`
- [ ] Au moins 1 courbe dans `reactor_curves`
- [ ] `math_input` en format math.js (pas Python, pas LaTeX)
- [ ] Tous les PNG listés en INPUT 3 sont associés à une courbe

---

*SCELLÉ — PENTERACT DORN V3 — VIIe Légion — 2026-05-29*
