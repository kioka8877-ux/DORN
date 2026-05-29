# META_CAMERA — Metaprompt Gemini
## Plan Caméra — DORN F02

> Statut : EN FORGE — À sceller

---

## Rôle

Ce metaprompt génère le bloc `camera_plan` à injecter dans `plan_de_vol.json`.
Prend une vidéo de référence et le JSON existant, produit les segments caméra.
S'exécute en chat manuel Gemini.

---

## Inputs Opérateur

1. `plan_de_vol.json` (produit par META_POLUX + validé F01)
2. Vidéo de référence ou description du style caméra souhaité

---

## Modes Caméra Disponibles

| mode | Usage |
|------|-------|
| static | Caméra fixe |
| follow_asset | Suit le PNG sur la courbe |
| follow_curve_tip | Suit l'extrémité de la courbe |
| wide_reveal | Zoom arrière — révélation globale |
| push_in | Zoom progressif vers la preuve |
| final_proof_lock | Dernière frame figée |

---

## Output Gemini Attendu

Bloc `camera_plan` JSON complet, prêt à injecter dans plan_de_vol.json.

---

*À sceller en Phase Forge.*
