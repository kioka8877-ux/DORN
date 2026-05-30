# DORN — CAMPAIGN LOG
## Carnet de Bord de Croisade

> *"Seek perfection of mind, body, and soul."* — Rogal Dorn

---

## Statut de la Flotte

| Frégate | Nom | Rôle | Statut | Date de Scellement |
|---------|-----|------|--------|--------------------|
| F01 | POLUX | Oracle & Curation → plan_de_vol.json | EN FORGE | — |
| F02 | CASTELLAN | HUD Contrôle + Sim. → plan_de_vol.json (figé) | EN FORGE | — |
| F03 | SIGISMUND | Réacteur Multi-Formes → video_render.mp4 | EN FORGE | — |
| F04A | INWIT | Viewer + Speed Control | EN FORGE | — |
| F04B | INWIT | FFmpeg Finishing → youtube_*.mp4 | EN FORGE | — |
| META | POLUX | Metaprompt Gemini (4 inputs) | EN FORGE | — |
| META | CAMERA | Metaprompt caméra | EN FORGE | — |

**Compteur de Guerre :**
```
[░░░░] 0/4 frégates scellées
[░░]   0/2 metaprompts scellés
[░░░░] 0/4 tests de production réussis
```

---

## CAMP_01 — AUDIT & BUGFIX — 2026-05-30

### Audit statique complet — 6 bugs identifiés et corrigés

| # | Fichier(s) | Bug | Severity | Commit |
|---|-----------|-----|----------|--------|
| 1 | `DRN_F04A.ipynb` cell-4, `DRN_F04B.ipynb` cell-5 | `--frigate F04A/F04B` invalides → argparse exit 2 | BLOQUANT | e008d22 |
| 2 | `drn_f03_sigismund.py` | `MODAL_WORKER_TEMPLATE.format()` crash IndexError — accolades Python non doublées | BLOQUANT | ce98d59 |
| 3 | `CurveTracer.jsx`, `AssetTracker.jsx` | `complexity_coefficient` absent de `revealFrames` → courbe gelée à 60% pour `wave_analysis` | VISUEL | 7c14c49 |
| 4 | `drn_f03_sigismund.py` | `.replace("e")` corrompt `_m.exp(` → regex `\be\b` | MINEUR | f6e46c5 |
| 5 | `VirtualCamera.jsx` | Mode `follow_curve_tip` non implémenté → caméra statique silencieuse | MINEUR | 079f463 |
| 6 | `DRN_F02.ipynb` cell-7 | `import os` absent → NameError si kernel redémarré | MINEUR | 2c050b4 |

### Fil d'Ariane — 2026-05-30

| Date | Frégate | Phase | Action | Validé |
|------|---------|-------|--------|--------|
| 2026-05-30 | F04 | AUDIT | Bug 1 : corriger appels CUSTOS F04A/F04B → F04 | ✓ |
| 2026-05-30 | F03 | AUDIT | Bug 2 : MODAL_WORKER_TEMPLATE accolades doublées | ✓ |
| 2026-05-30 | F03 | AUDIT | Bug 3 : complexity_coefficient dans CurveTracer + AssetTracker | ✓ |
| 2026-05-30 | F03 | AUDIT | Bug 4 : compute_y_range replace('e') → regex \be\b | ✓ |
| 2026-05-30 | F03 | AUDIT | Bug 5 : follow_curve_tip implémenté dans VirtualCamera | ✓ |
| 2026-05-30 | F02 | AUDIT | Bug 6 : import os ajouté en CELL 7 DRN_F02.ipynb | ✓ |

### État post-audit

- Mode `--mode direct` F03 : **PRÊT** (seul le bug 2 bloquait Modal)
- F04A + F04B check-in CUSTOS : **CORRIGÉS** (bug 1)
- `wave_analysis` engine_type : **CORRIGÉ** (bug 3)
- `geometric_construction` + `single_proof` camera : **CORRIGÉS** (bug 5)
- Tous les engine_types : **OPÉRATIONNELS**

---

## CAMP_00 — INITIALISATION — 2026-05-29

Structure du repo initialisée. Directive Impériale V3 scellée.
Toutes les frégates en phase de FORGE.

---

## Flux de Données DORN

```
META_POLUX (Gemini chat, 4 inputs)
  └─► plan_de_vol.json ──────────────────► F01 IN/
                                            F02 IN/ (après F01)

META_CAMERA (Gemini chat)
  └─► camera_plan injecté dans JSON ──────► F02 IN/

F01 POLUX    OUT/ plan_de_vol.json ─────► F02 IN/
F02 CASTELLAN OUT/ plan_de_vol.json ────► F03 IN/
F03 SIGISMUND OUT/ video_render.mp4 ────► F04 IN/
F04 INWIT     OUT/ youtube_*.mp4 ───────► Téléchargement opérateur
```

---

## Héritage CRUSADER — Éléments Portés (Coût Déjà Payé)

Ces éléments sont copiés/adaptés depuis CRUSADER et ne seront PAS développés from scratch.
Ils ont été validés en conditions de production réelles dans CRUSADER.

| Élément | Frégates DORN | Origine CRUSADER | Commentaire |
|---------|---------------|------------------|-------------|
| `calculateMetadata` Remotion | F03 | F03 SIGISMUND | Durée dynamique depuis JSON → adapté pour timing DORN |
| `--gl swangle` flag | F03 | F03 SIGISMUND | Rendu logiciel Colab — copie directe |
| Modal chunking 3 workers | F03 | F03/crs_f03_modal_worker.py | Adapter les inputs (plan_de_vol.json vs timing+roadmap) |
| Architecture src/ Remotion | F03 | F03 src/ (Root, Main, components) | Reécrire les composants (SVG math vs stickman) |
| FFmpeg pipeline F04 | F04B | F04/crs_f04_helbrecht.py | Copie quasi-directe + ajout setpts conditionnel (V3) |
| `validated_by_magos: true` | F02 | F02 CASTELLAN | Pattern de validation identique |
| `CRS_CUSTOS.py` | Toutes | CRS_CUSTOS.py | Adapté pour les frégates et schémas JSON DORN |
| IN/ → CODEBASE/ → OUT/ structure | Toutes | Toutes | Architecture identique |

**Ce qui est NOUVEAU (from scratch) :**
- F01 POLUX — validation JSON + strip EXIF (pas d'équivalent dans CRUSADER)
- F02 CASTELLAN — Streamlit + Canvas JS (vs Flask + HTML natif CRUSADER)
- F03 composants JSX — MathInterpreter, CurveTracer, AssetTracker, VirtualCamera (SVG neon vs stickman)
- F04A INWIT — Viewer HTML + sélecteur vitesse (nouveau en V3)
- META_POLUX / META_CAMERA — Metaprompts DORN

---

## Rites du Sang — Principes Gouvernants

1. **Gratuit** — Aucun API payant, aucune dépendance commerciale
2. **Colab-first** — Tout s'exécute sur Google Colab, le PC est une télécommande
3. **60 fps** — Standard DORN, timing dynamique (la math dicte la durée)
4. **Dual format** — Vertical 1080×1920 (Shorts) et Horizontal 1920×1080 (Long-form)
5. **Isolation des frégates** — Chaque frégate opère en silo, lit son IN/, écrit son OUT/
6. **Transfert validé** — Tout transit inter-frégate passe par CRS_CUSTOS.py (check-out + check-in)
7. **Paradigme timing dynamique** — La math dicte la durée via calculateMetadata [AXIOME DORN V3]

---

## Décisions de Forge (Axiomes)

| Date | Décision | Justification |
|------|----------|---------------|
| 2026-05-29 | 60 fps fixe (vs 30 fps CRUSADER) | Visualisations mathématiques fluides, curves SVG |
| 2026-05-29 | Streamlit pour F02 (vs Flask CRUSADER) | Canvas JS natif Streamlit, pas de HTML custom |
| 2026-05-29 | Timing dynamique (math → durée) | Paradigme inversion TRIZ : la courbe dicte la composition |
| 2026-05-29 | step_per_frame calculé par Gemini | Operateur donne durée cible, Gemini fait le calcul |
| 2026-05-29 | F04 scindé F04A + F04B | Viewer de validation vitesse avant encoding final |
| 2026-05-29 | playback_speed 1.0 → FFmpeg setpts conditionnel | Si speed=1.0, skip re-encode — qualité préservée |
| 2026-05-29 | complexity_coefficient par engine_type | Gemini adapte le rythme selon la complexité visuelle |
| 2026-05-29 | Modal chunking hérité de CRUSADER | 17h de débogage économisées — même pattern |
| 2026-05-29 | CRS_CUSTOS.py adapté (pas réécrit) | Architecture de validation identique, seuls les chemins changent |

---

## Fil d'Ariane — Log Chronologique

| Date | Frégate | Phase | Action | Validé |
|------|---------|-------|--------|--------|
| 2026-05-29 | — | INIT | Création du repo DORN sur GitHub | ✓ |
| 2026-05-29 | — | INIT | Structure des frégates initialisée | ✓ |
| 2026-05-29 | — | INIT | Directive Impériale V3 scellée (PDF) | ✓ |
| 2026-05-29 | — | INIT | CRS_CUSTOS.py adapté depuis CRUSADER | ✓ |

---

## F01 — POLUX
- Rôle : Validation plan_de_vol.json + strip EXIF PNG
- Stack : Python stdlib + Pillow (EXIF)
- IN: plan_de_vol.json + images/*.png | OUT: plan_de_vol.json (valide) + images/*.png (propres)
- Statut : EN FORGE

## F02 — CASTELLAN
- Rôle : HUD Streamlit + Canvas JS, simulation courbes, validation JSON
- Stack : Streamlit + math.js CDN + Canvas JS
- IN: plan_de_vol.json + images/*.png | OUT: plan_de_vol.json (figé, validated_by_magos)
- Statut : EN FORGE

## F03 — SIGISMUND
- Rôle : Rendu Remotion SVG neon 60fps (timing dynamique)
- Stack : Remotion 4.x + React + Modal chunking (hérité CRUSADER)
- IN: plan_de_vol.json (figé) + images/*.png | OUT: video_render.mp4
- Statut : EN FORGE
- Note : calculateMetadata, --gl swangle, Modal chunking — portés depuis CRUSADER

## F04A/B — INWIT
- Rôle : F04A = viewer HTML Colab + sélecteur vitesse ; F04B = FFmpeg finishing
- Stack : HTML/JS natif + FFmpeg
- IN: video_render.mp4 + plan_de_vol.json | OUT: youtube_short/long.mp4
- Statut : EN FORGE
- Note : Pipeline FFmpeg hérité de F04 HELBRECHT CRUSADER + setpts conditionnel (nouveau)

## METAPROMPTS
- META_POLUX.md — 4 inputs opérateur + calcul step_per_frame par Gemini
- META_CAMERA.md — Plan caméra depuis vidéo de référence
- Statut : EN FORGE
