# META_POLUX — Metaprompt Gemini / Claude
## Oracle & Curation — PENTERACT DORN F01
### STATUT : SCELLÉ — V5 — 2026-06-06

---

## Rôle

Ce metaprompt est la **porte d'entrée absolue** du pipeline PENTERACT DORN.
Il transforme un concept pop-culture en `plan_de_vol.json` V3 complet et exploitable,
ainsi que les métadonnées YouTube prêtes à copier-coller.

**S'exécute en chat manuel Gemini ou Claude — aucun appel API dans le code.**

---

## Instructions d'utilisation

1. Ouvre Gemini (chat.google.com ou Gemini Advanced) ou Claude (claude.ai)
2. Copie-colle le bloc **PROMPT** ci-dessous en entier
3. Remplace les balises `[INPUT_X]` par tes réponses réelles
4. INPUT_5 est **optionnel** — si tu n'as pas de vidéo de référence, laisse la balise vide ou supprime le bloc
5. Envoie — le modèle génère le `plan_de_vol.json` complet + les métadonnées YouTube

---

## Les 5 Inputs Opérateur

| # | Balise | Question | Exemple | Statut |
|---|--------|----------|---------|--------|
| 1 | `[INPUT_1]` | Sujet + thèse en 1 phrase | `Messi est meilleur que CR7 grâce à son centre de gravité bas` | Obligatoire |
| 2 | `[INPUT_2]` | Réponse mathématique souhaitée | `Montrer que stabilité = f(hauteur centre de gravité)` | Obligatoire |
| 3 | `[INPUT_3]` | Assets PNG ou JPEG disponibles (noms de fichiers) | `messi_head.png, cr7_head.jpg` | Obligatoire |
| 4 | `[INPUT_4]` | Durée cible de la vidéo | `30 secondes` / `45 secondes` / `1 minute` | Obligatoire |
| 5 | `[INPUT_5]` | URL ou fichier vidéo de référence cinématique | `https://youtube.com/watch?v=xxxxx` | **Optionnel** |

---

## PROMPT (copier-coller intégral)

```
Tu es l'Oracle POLUX du pipeline PENTERACT DORN — un système de visualisation mathématique
Pop-Science Culture pour YouTube Shorts / TikTok.

Ta mission : transformer le concept ci-dessous en un plan_de_vol.json V3 complet et prêt
à entrer dans le pipeline de production, ainsi que les métadonnées YouTube associées.

=== INPUTS OPÉRATEUR ===

INPUT 1 — Sujet + thèse :
[INPUT_1]

INPUT 2 — Réponse mathématique souhaitée :
[INPUT_2]

INPUT 3 — Assets PNG ou JPEG disponibles :
[INPUT_3]

INPUT 4 — Durée cible :
[INPUT_4]

INPUT 5 — Vidéo de référence cinématique (optionnel) :
[INPUT_5]

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

ÉTAPE 4 — Génération du hook viral et des métadonnées concept
- title : accroche courte, choc émotionnel
  → Maximum 45 caractères (emoji inclus)
  → Si format = "vertical" : titre ultra-court, tension maximale, emoji final
    Structure : Hook + Sujet + Bait + emoji  (ex: "La Physique Prouve Messi Imbattable 🧲")
  → Si format = "horizontal" : titre plus descriptif avec sujet + révélation + emoji
    Structure : Hook + Sujet + Bait + emoji  (ex: "La Physique Explique Pourquoi Messi Domine CR7 🔬")
- hook : 1 phrase d'accroche narrative (tension + révélation mathématique)
- thesis : la thèse mathématique en 1 phrase technique

ÉTAPE 5 — Génération du camera_plan
Cette étape génère le plan caméra intégré directement dans le JSON.
META_CAMERA est supprimé — tout se génère ici en une seule passe.

5a — Calcul des bornes temporelles
  reveal_frames = round((x_range.end - x_range.start) / step_per_frame)
  total_frames = round(reveal_frames * complexity_coefficient) + final_freeze_frames
  freeze_start = total_frames - final_freeze_frames

5b — Détermination du movement_energy
  Si INPUT_5 est fourni (URL ou fichier vidéo) :
    Regarde la vidéo et analyse :
    - L'intensité des mouvements de caméra (lent et posé / fluide et narratif / vif et dynamique / ultra-rapide avec cuts)
    - La fréquence des changements de plan
    - L'intensité du shake (tremblement)
    - Le comportement du zoom (progressif / brusque / absent)
    Déduis le movement_energy parmi : "calm" / "cinematic" / "aggressive" / "viral_edit"
    Déduis shake_intensity entre 0.0 et 0.15

  Si INPUT_5 est absent :
    movement_energy = "cinematic" par défaut
    shake_intensity = 0.08 par défaut

5c — Construction des segments selon engine_type

  time_evolution_comparison (3 segments) :
    SEG 1 [0 → round(reveal_frames * 0.7)]         : follow_asset sur la courbe dominante, zoom 1.15, shake 0.03
    SEG 2 [suite → freeze_start]                   : wide_reveal (montre l'écart), zoom 0.95, shake 0.02
    SEG 3 [freeze_start → total_frames]            : final_proof_lock, zoom 1.0, shake 0.0

  geometric_construction (3 segments) :
    SEG 1 [0 → round(reveal_frames * 0.5)]         : follow_curve_tip, zoom 1.2, shake 0.02
    SEG 2 [suite → freeze_start]                   : wide_reveal, zoom 0.9, shake 0.01
    SEG 3 [freeze_start → total_frames]            : final_proof_lock, zoom 1.0, shake 0.0

  wave_analysis (2 segments) :
    SEG 1 [0 → freeze_start]                       : static, zoom 1.0, shake 0.0
    SEG 2 [freeze_start → total_frames]            : final_proof_lock, zoom 1.0, shake 0.0

  single_proof (3 segments) :
    SEG 1 [0 → round(reveal_frames * 0.6)]         : follow_curve_tip, zoom 1.1, shake 0.02
    SEG 2 [suite → freeze_start]                   : push_in, zoom 1.3, shake 0.03
    SEG 3 [freeze_start → total_frames]            : final_proof_lock, zoom 1.0, shake 0.0

  Si movement_energy = "viral_edit" : appliquer shake entre 0.08 et 0.12 sur tous les segments sauf final_proof_lock.
  Si movement_energy = "calm" : réduire tous les shake à 0.0 ou 0.01, zoom plus proche de 1.0.
  Si movement_energy = "aggressive" : augmenter shake à 0.08–0.12, zoom plus marqué sur SEG 1.

5d — Règles impératives camera_plan
  - Le dernier segment DOIT toujours être mode "final_proof_lock", shake 0.0
  - start_frame du dernier segment = freeze_start
  - end_frame du dernier segment = total_frames
  - Les segments couvrent [0, total_frames] sans trou ni chevauchement
  - zoom entre 0.9 et 1.5 — shake entre 0.0 et 0.15 — x_offset et y_offset entre -100 et 100
  - target_curve_id rempli uniquement pour follow_asset et follow_curve_tip

ÉTAPE 6 — Attribution des assets PNG ou JPEG
Pour chaque fichier PNG, JPG ou JPEG listé en INPUT 3, associe-le à la courbe la plus pertinente.
`asset_filename` accepte les extensions `.png`, `.jpg`, `.jpeg`.
scale_factor = 1.2, auto_rotate_slope = true, inertia_smooth = 0.1

ÉTAPE 7 — Génération de la final_frame
- annotation : texte de conclusion mathématique court (15 mots max)
- freeze_duration_frames = 90 (fixe)

ÉTAPE 8 — Audio
- wave_type = "sine"
- base_frequency_hz = 220
- frequency_multiplier = 12.0

ÉTAPE 9 — Génération des métadonnées YouTube
Génère le bloc `youtube_metadata` avec les règles suivantes.

Champ `title` :
- Reprend le title généré à l'Étape 4 (déjà ≤ 45 chars, avec emoji)

Champ `hashtags` — exactement 3 entrées :
- 1 broad short-tail : mot-clé large de la niche (ex: #football, #math, #physique)
- 2 long-tail niche : expressions précises extraites de INPUT_1
  (ex: #centreDeGravite, #biomecaniqueFootball)
- Format : #CamelCase, sans espace, sans caractères spéciaux

Champ `description` — 4 blocs séparés par une ligne vide :

BLOC 1 — SEO Hook (en français)
Rédige 2-3 phrases captivantes à partir de `title`, `hook` et `thesis`.
Intègre naturellement des mots-clés liés au sujet de INPUT_1.
Objectif : accrocher le lecteur et améliorer le référencement.

BLOC 2 — Déclaration d'Œuvre Originale (en anglais — texte fixe)
Every video on this channel is unique and produced from mathematical calculations performed entirely by hand.
All animations are created from scratch using our own custom-built tools — no templates, no stock footage.
This content is the exclusive intellectual property of this channel.
Any reproduction, re-upload, or redistribution without the explicit written consent of the creator is strictly prohibited.
These videos reflect the work of an independent creator who personally conceives, calculates, and animates every frame.

BLOC 3 — Hashtags
Les 3 hashtags du champ `hashtags`, séparés par un espace.

BLOC 4 — Tags SEO cachés (français + anglais)
Liste de 8 à 12 mots-clés sans `#`, séparés par des espaces.
Extraits du sujet (INPUT_1), de la niche mathématique, des courbes, et du format vidéo.

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
    "camera_signature": "DORN_META_POLUX_V5",
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
  },
  "youtube_metadata": {
    "title": "",
    "hashtags": ["", "", ""],
    "description": ""
  }
}
```

---

## Exemple de Sortie Attendue (Messi vs CR7 — 30 secondes — sans vidéo référence)

```json
{
  "matrix_signature": "PENTERACT_DORN_VII_LEGION",
  "concept_metadata": {
    "title": "La Physique Prouve Messi Imbattable 🧲",
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
        "asset_filename": "cr7_head.jpg",
        "scale_factor": 1.2,
        "physics": {
          "auto_rotate_slope": true,
          "inertia_smooth": 0.1
        }
      }
    }
  ],
  "camera_plan": {
    "camera_signature": "DORN_META_POLUX_V5",
    "global_style": {
      "movement_energy": "cinematic",
      "default_easing": "easeInOutCubic",
      "shake_intensity": 0.08
    },
    "camera_segments": [
      {
        "start_frame": 0,
        "end_frame": 1134,
        "mode": "follow_asset",
        "target_curve_id": "messi",
        "zoom": 1.15,
        "x_offset": 0,
        "y_offset": -40,
        "shake": 0.03
      },
      {
        "start_frame": 1134,
        "end_frame": 1620,
        "mode": "wide_reveal",
        "target_curve_id": "",
        "zoom": 0.95,
        "x_offset": 0,
        "y_offset": 0,
        "shake": 0.02
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
  },
  "youtube_metadata": {
    "title": "La Physique Prouve Messi Imbattable 🧲",
    "hashtags": ["#football", "#centreDeGravite", "#biomecaniqueFootball"],
    "description": "La physique a enfin tranché le débat Messi vs CR7. Découvrez comment la biomécanique révèle que la stabilité est une fonction mathématique directe de la hauteur du centre de gravité — et pourquoi Messi gagne à tout coup.\n\nEvery video on this channel is unique and produced from mathematical calculations performed entirely by hand.\nAll animations are created from scratch using our own custom-built tools — no templates, no stock footage.\nThis content is the exclusive intellectual property of this channel.\nAny reproduction, re-upload, or redistribution without the explicit written consent of the creator is strictly prohibited.\nThese videos reflect the work of an independent creator who personally conceives, calculates, and animates every frame.\n\n#football #centreDeGravite #biomecaniqueFootball\n\nmessi cristiano stabilité biomécanique physique football mathématiques courbe sigmoid viral centre gravité"
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
- [ ] Tous les PNG/JPEG listés en INPUT 3 sont associés à une courbe
- [ ] `camera_plan` présent — segments couvrent [0, total_frames], dernier segment = `final_proof_lock`, shake = 0.0
- [ ] `camera_signature` = `"DORN_META_POLUX_V5"`
- [ ] `youtube_metadata` présent — titre ≤ 45 chars, 3 hashtags, description 4 blocs

---

## Modes caméra disponibles (référence F03)

| mode | Comportement dans VirtualCamera.jsx |
|------|-------------------------------------|
| `static` | Caméra fixe, aucun mouvement |
| `follow_asset` | Suit le PNG attaché à une courbe |
| `follow_curve_tip` | Suit l'extrémité mathématique de la courbe |
| `wide_reveal` | Zoom arrière progressif — révèle la construction complète |
| `push_in` | Zoom progressif vers la preuve finale |
| `final_proof_lock` | Dernière frame figée — aucun mouvement, shake 0.0 |

---

*SCELLÉ — PENTERACT DORN V5 — VIIe Légion — 2026-06-06*
