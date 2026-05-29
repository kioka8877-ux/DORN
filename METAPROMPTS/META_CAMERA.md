# META_CAMERA — Metaprompt Gemini
## Plan Caméra — PENTERACT DORN F02
### STATUT : SCELLÉ — V3 — 2026-05-29

---

## Rôle

Ce metaprompt génère le bloc `camera_plan` à injecter dans `plan_de_vol.json`.
Il prend le JSON produit par META_POLUX (validé par F01) et un style caméra,
puis calcule des segments caméra cohérents avec la narrative mathématique.

**S'exécute en chat manuel Gemini — après F01, avant F02.**

---

## Instructions d'utilisation

1. Ouvre Gemini (chat.google.com ou Gemini Advanced)
2. Copie-colle le bloc **PROMPT GEMINI** ci-dessous en entier
3. Colle ton `plan_de_vol.json` (sortie F01) à la place de `[INPUT_JSON]`
4. Décris le style caméra à la place de `[INPUT_STYLE]`
5. Envoie — Gemini génère le bloc `camera_plan` complet
6. Copie le bloc `camera_plan` et injecte-le dans ton JSON (remplace le `camera_plan` existant)

---

## Les 2 Inputs Opérateur

| # | Balise | Contenu | Exemple |
|---|--------|---------|---------|
| 1 | `[INPUT_JSON]` | Le `plan_de_vol.json` complet sorti de F01 | Coller le JSON entier |
| 2 | `[INPUT_STYLE]` | Description du style caméra souhaité | `"Dynamique, suit Messi, zoom final sur l'écart"` |

### Styles caméra prédéfinis (utiliser tel quel dans INPUT_STYLE)

| Style | Effet | Idéal pour |
|-------|-------|-----------|
| `"Cinématique classique"` | Suit le PNG principal, zoom progressif | time_evolution_comparison |
| `"Révélation épique"` | Zoom arrière → révèle tout → lock final | geometric_construction |
| `"Analyse d'onde"` | Caméra fixe, panoramique horizontal | wave_analysis |
| `"Preuve dramatique"` | Push in progressif → freeze sur la preuve | single_proof |
| `"Viral edit"` | Mouvements rapides, shake, cuts dynamiques | Tous formats courts |

---

## PROMPT GEMINI (copier-coller intégral)

```
Tu es le directeur de la photographie virtuelle du pipeline PENTERACT DORN.
Ta mission : analyser le plan_de_vol.json ci-dessous et générer un bloc camera_plan
qui maximise l'impact narratif de la visualisation mathématique.

=== INPUT 1 — plan_de_vol.json ===

[INPUT_JSON]

=== INPUT 2 — Style caméra souhaité ===

[INPUT_STYLE]

=== RÈGLES DE GÉNÉRATION ===

ÉTAPE 1 — Lecture du JSON
Extrais ces valeurs du JSON fourni :
- engine_type (dans concept_metadata)
- fps (dans timing)
- step_per_frame (dans timing)
- x_range (dans timing)
- complexity_coefficient (dans timing)
- final_freeze_frames (dans timing)
- IDs des courbes (dans reactor_curves[].id)
- ID du premier asset PNG (dans reactor_curves[0].tracking_target.asset_filename)

ÉTAPE 2 — Calcul du nombre total de frames
reveal_frames = round((x_range.end - x_range.start) / step_per_frame)
total_frames = round(reveal_frames * complexity_coefficient) + final_freeze_frames
freeze_start = total_frames - final_freeze_frames

ÉTAPE 3 — Choix du movement_energy selon engine_type et style demandé
- time_evolution_comparison + cinématique → "cinematic"
- geometric_construction               → "calm" ou "cinematic"
- wave_analysis                        → "calm"
- single_proof                         → "cinematic" ou "aggressive"
- style "viral edit" → "viral_edit" quel que soit l'engine_type

ÉTAPE 4 — Construction des segments caméra
Règles impératives :
- Le dernier segment DOIT toujours être mode "final_proof_lock"
  avec start_frame = freeze_start, end_frame = total_frames
- Les segments doivent couvrir [0, total_frames] sans trou ni chevauchement
- Minimum 2 segments, maximum 5 segments
- zoom entre 0.9 et 1.5
- shake entre 0.0 et 0.15 (0.0 pour final_proof_lock)
- x_offset et y_offset entre -100 et 100

Logique recommandée par engine_type :

time_evolution_comparison (2-3 segments) :
  SEG 1 [0 → reveal_frames*0.7]    : follow_asset sur la courbe dominante, zoom 1.15
  SEG 2 [*0.7 → freeze_start]      : wide_reveal pour montrer l'écart entre courbes, zoom 0.95
  SEG 3 [freeze_start → total]     : final_proof_lock, zoom 1.0

geometric_construction (3 segments) :
  SEG 1 [0 → reveal_frames*0.5]    : follow_curve_tip, zoom 1.2
  SEG 2 [*0.5 → freeze_start]      : wide_reveal, zoom 0.9
  SEG 3 [freeze_start → total]     : final_proof_lock, zoom 1.0

wave_analysis (2 segments) :
  SEG 1 [0 → freeze_start]         : static, zoom 1.0 (toute la vague visible)
  SEG 2 [freeze_start → total]     : final_proof_lock, zoom 1.0

single_proof (3 segments) :
  SEG 1 [0 → reveal_frames*0.6]    : follow_curve_tip, zoom 1.1
  SEG 2 [*0.6 → freeze_start]      : push_in, zoom progressif 1.3
  SEG 3 [freeze_start → total]     : final_proof_lock, zoom 1.0

Si style "viral_edit" : ajouter shake 0.08-0.12 sur tous les segments sauf final_proof_lock.

ÉTAPE 5 — Format de sortie
Retourne UNIQUEMENT le bloc JSON camera_plan ci-dessous, sans texte avant ni après.

{
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
        "zoom": 1.0,
        "x_offset": 0,
        "y_offset": 0,
        "shake": 0.0
      }
    ]
  }
}
```

---

## Modes caméra disponibles

| mode | Comportement dans VirtualCamera.jsx |
|------|-------------------------------------|
| `static` | Caméra fixe, aucun mouvement |
| `follow_asset` | Suit le PNG attaché à une courbe (CSS transform suit l'asset) |
| `follow_curve_tip` | Suit l'extrémité mathématique de la courbe (x courant) |
| `wide_reveal` | Zoom arrière progressif pour révéler la construction complète |
| `push_in` | Zoom progressif vers la preuve finale |
| `final_proof_lock` | Dernière frame figée — propre, lisible, aucun mouvement |

---

## Exemple de Sortie Attendue (Messi vs CR7 — 30 secondes — cinématique)

Pour `total_frames = 1800`, `freeze_start = 1620`, courbe principale `"messi"` :

```json
{
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
  }
}
```

---

## Vérification avant injection dans le JSON

- [ ] Dernier segment = `"final_proof_lock"`
- [ ] `start_frame` du dernier segment = `total_frames - final_freeze_frames`
- [ ] Segments couvrent `[0, total_frames]` sans trou
- [ ] Aucun `shake` sur `final_proof_lock`
- [ ] `target_curve_id` rempli pour `follow_asset` et `follow_curve_tip`

## Injection dans le JSON

Une fois le bloc `camera_plan` validé, remplace le champ `camera_plan` dans ton
`plan_de_vol.json` (sorti de F01/OUT/) par ce nouveau bloc.
Le fichier mis à jour entre dans `F02_CASTELLAN/IN/`.

---

*SCELLÉ — PENTERACT DORN V3 — VIIe Légion — 2026-05-29*
