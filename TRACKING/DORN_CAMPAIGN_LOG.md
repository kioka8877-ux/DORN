# DORN — CAMPAIGN LOG
## Carnet de Bord de Croisade

> *"Seek perfection of mind, body, and soul."* — Rogal Dorn

---

## Statut de la Flotte

| Frégate | Nom | Rôle | Statut | Date de Scellement |
|---------|-----|------|--------|--------------------|
| F01 | POLUX | Oracle & Curation → plan_de_vol.json | SCELLÉ ✓ | 2026-05-31 |
| F02 | CASTELLAN | HUD Contrôle + Sim. → plan_de_vol.json (figé) | SCELLÉ ✓ | 2026-06-05 |
| F03 | SIGISMUND | Réacteur Multi-Formes → video_render.mp4 | SCELLÉ ✓ | 2026-06-05 |
| F04A | INWIT | Viewer + Speed Control | SCELLÉ ✓ | 2026-06-05 |
| F04B | INWIT | FFmpeg Finishing → youtube_*.mp4 | SCELLÉ ✓ | 2026-06-05 |
| META | POLUX | Metaprompt Gemini/Claude (5 inputs — camera intégré) | EN FORGE — V5 en cours | — |

**Compteur de Guerre :**
```
[████] 4/4 frégates scellées ██████████ 100%
[░]    0/1 metaprompt scellé (META_CAMERA absorbé dans V5)
[████] 4/4 tests de production réussis ██████████ 100%
```

## ██████████████████████████████████████████
## ██  PROJET DORN — SCELLÉ DANS SON ENTIER  ██
## ██████████████████████████████████████████

> *"By the Emperor's will and the iron of Dorn, the VII Legion stands eternal."*

**LA FLOTTE EST COMPLÈTE. LA CROISADE EST VICTORIEUSE.**

**PAR LA VOLONTÉ DE L'EMPEREUR ET DE ROGAL DORN.**
**PAR LE BRAS DE SIGISMUND, SON CHAMPION.**
**PAR LA VIGILANCE D'INWIT, SON BASTION.**

---

## CAMP_05 — TEST DE PRODUCTION F04 — 2026-06-05

### F04A INWIT — Test de Production

| # | Etape | Résultat | Note |
|---|-------|----------|------|
| 1 | Montage Drive | ✓ OK | Drive monté |
| 2 | Configuration DRIVE_BASE | ✓ OK | Chemin validé |
| 3 | Script copié | ✓ OK | drn_f04a_inwit.py |
| 4 | Vidéo encodée pour affichage | ✓ OK | 2 MB chargés |
| 5 | Viewer HUD lancé | ✓ OK | Vitesse courante : 1.0x |
| 6 | Vitesse figée | ✓ OK | 0.5x — validated=True |
| 7 | CRS_CUSTOS check-out F04 | ✓ OK | Transit F04A→F04B autorisé |

**F04A INWIT — SCELLÉ.**

### F04B INWIT — Test de Production

| # | Etape | Résultat | Note |
|---|-------|----------|------|
| 1 | Montage Drive | ✓ OK | |
| 2 | Configuration DRIVE_BASE | ✓ OK | |
| 3 | FFmpeg disponible + vitesse figée | ✓ OK | 0.5x confirmé depuis speed_lock.json |
| 4 | FFmpeg Finishing — re-encode | ✓ OK | setpts=PTS/0.5 appliqué |
| 5 | CRS_CUSTOS check-in F04 | ✓ OK | Scellement final |

**Contrôle qualité youtube_short.mp4 :**

| Contrôle | Résultat |
|----------|----------|
| Taille | 3.50 MB ✓ |
| Container | MP4/ISO Base Media (isom) ✓ |
| Codec vidéo | H.264/AVC (x264) ✓ |
| Tag `©too` | `Lavf58.76.100` — camouflage FFmpeg standard ✓ |
| Tags projet (DORN, PENTERACT, SIGISMUND...) | Aucun ✓ |
| Tags sensibles (title, artist, comment, date) | Aucun ✓ |
| Boxes suspectes | Aucune ✓ |

**F04B INWIT — SCELLÉ.**

### Fil d'Ariane — 2026-06-05

| Date | Frégate | Phase | Action | Validé |
|------|---------|-------|--------|--------|
| 2026-06-05 | F04A | PROD | Test de production complet | ✓ |
| 2026-06-05 | F04A | PROD | Vitesse figée 0.5x — CRS_CUSTOS check-out | ✓ |
| 2026-06-05 | F04A | SCELLEMENT | F04A INWIT scellé | ✓ |
| 2026-06-05 | F04B | PROD | FFmpeg Finishing — setpts=PTS/0.5 | ✓ |
| 2026-06-05 | F04B | PROD | Contrôle qualité youtube_short.mp4 — PROPRE | ✓ |
| 2026-06-05 | F04B | SCELLEMENT | F04B INWIT scellé | ✓ |
| 2026-06-06 | META_POLUX | FORGE | META_POLUX V4 → V5 : ÉTAPE 5 caméra intégrée, 5 inputs | ✓ |
| 2026-06-06 | META_CAMERA | SUPPRESSION | META_CAMERA.md supprimé — absorbé dans META_POLUX V5 | ✓ |
| 2026-06-05 | DORN | SCELLEMENT | PROJET DORN SCELLÉ DANS SON ENTIER | ✓ |

---

## CAMP_04 — TEST DE PRODUCTION F02 — 2026-06-05

### F02 CASTELLAN — Test de Production

| # | Cellule | Résultat | Note |
|---|---------|----------|------|
| 1 | Streamlit + Canvas JS — lancement | ✓ OK | Interface HUD opérationnelle |
| 2 | Chargement plan_de_vol.json | ✓ OK | Lecture + validation JSON |
| 3 | Simulation courbes math.js | ✓ OK | Rendu Canvas temps réel |
| 4 | Injection camera_plan | ✓ OK | Bloc caméra intégré au JSON |
| 5 | validated_by_magos: true — sauvegarde | ✓ OK | JSON figé et signé |
| 6 | CRS_CUSTOS check-out F02 | ✓ OK | Transit F02→F03 autorisé |

**F02 CASTELLAN — SCELLÉ. PAR LA VOLONTÉ DE L'EMPEREUR ET DE ROGAL DORN.**

> *"Hold the line. Every wall is sacred."* — Castellan des Fists Impériaux

### Fil d'Ariane — 2026-06-05

| Date | Frégate | Phase | Action | Validé |
|------|---------|-------|--------|--------|
| 2026-06-05 | F02 | PROD | Test de production complet — 6 cellules | ✓ |
| 2026-06-05 | F02 | PROD | validated_by_magos: true — JSON figé | ✓ |
| 2026-06-05 | F02 | PROD | CRS_CUSTOS check-out F02 — OK | ✓ |
| 2026-06-05 | F02 | SCELLEMENT | F02 CASTELLAN scellé | ✓ |

---

## CAMP_03 — TEST DE PRODUCTION F03 — 2026-06-05

### F03 SIGISMUND — Test de Production

| # | Cellule | Résultat | Note |
|---|---------|----------|------|
| 1 | Dépendances Remotion + React | ✓ OK | Build GitHub Actions réussi |
| 2 | calculateMetadata — durée dynamique | ✓ OK | Durée calculée depuis plan_de_vol.json |
| 3 | CurveTracer — rendu SVG neon | ✓ OK | Toutes les courbes tracées |
| 4 | AssetTracker — images PNG/JPEG | ✓ OK | Assets servis depuis public/IN/ |
| 5 | VirtualCamera — modes caméra | ✓ OK | follow_curve_tip, static, wide_reveal |
| 6 | MathInterpreter — expressions math.js | ✓ OK | eval sécurisé, polar + cartesian |
| 7 | rendu final video_render.mp4 | ✓ OK | 60 fps, dual format vertical/horizontal |

**Bugfix identifié en production :**

| # | Composant | Bug | Fix |
|---|-----------|-----|-----|
| 7 | `AssetTracker.jsx` | Images PNG/JPEG non affichées — assets doivent être dans `CODEBASE/public/IN/` | Assets copiés via `setup_public_assets()` — PNG et JPEG supportés |

**F03 SIGISMUND — SCELLÉ. PAR LA VOLONTÉ DE L'EMPEREUR ET DE SON CHAMPION SIGISMUND.**

> *"The only true failure is to stop fighting."* — Sigismund, Premier Capitaine des Fists Impériaux

### Fil d'Ariane — 2026-06-05

| Date | Frégate | Phase | Action | Validé |
|------|---------|-------|--------|--------|
| 2026-06-05 | F03 | PROD | Test de production complet — 7 cellules | ✓ |
| 2026-06-05 | F03 | PROD | Bugfix #7 : AssetTracker images PNG/JPEG → public/IN/ | ✓ |
| 2026-06-05 | F03 | PROD | video_render.mp4 rendu 60fps — VALIDÉ | ✓ |
| 2026-06-05 | F03 | SCELLEMENT | F03 SIGISMUND scellé | ✓ |

---

## CAMP_02 — TEST DE PRODUCTION F01 — 2026-05-31

### F01 POLUX — Test de Production

| # | Cellule | Résultat | Note |
|---|---------|----------|------|
| 1 | CELL 1 — Mount Drive | ✓ OK | Drive monté |
| 2 | CELL 2 — Init structure + scripts | ✓ OK | Dépôt rendu public, scripts téléchargés |
| 3 | CELL 3 — Drive base | ✓ OK | |
| 4 | CELL 4 — Pillow | ✓ OK | |
| 5 | CELL 5 — Copy script | ✓ OK | |
| 6 | CELL 6 — drn_f01_polux.py | ✓ VALIDATION OK | plan_de_vol.json + images IN requis |
| 7 | CELL 7 — CRS_CUSTOS check-in F01 | ✓ CHECK-IN OK | Transit F01→F02 autorisé |

**F01 POLUX — SCELLÉ. PAR LA VOLONTÉ DE L'EMPEREUR ET DE ROGAL DORN.**

### Fil d'Ariane — 2026-05-31

| Date | Frégate | Phase | Action | Validé |
|------|---------|-------|--------|--------|
| 2026-05-31 | F01 | PROD | Test de production complet — 7 cellules | ✓ |
| 2026-05-31 | F01 | PROD | drn_f01_polux.py — VALIDATION OK | ✓ |
| 2026-05-31 | F01 | PROD | CRS_CUSTOS check-in F01 — OK | ✓ |
| 2026-05-31 | F01 | SCELLEMENT | F01 POLUX scellé | ✓ |

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

---

## CAMP_00 — INITIALISATION — 2026-05-29

Structure du repo initialisée. Directive Impériale V3 scellée.
Toutes les frégates en phase de FORGE.

---

## Flux de Données DORN

```
META_POLUX (Gemini/Claude chat, 5 inputs — camera_plan intégré)
  └─► plan_de_vol.json (math + camera) ────► F01 IN/
                                            F02 IN/ (après F01)

F01 POLUX    OUT/ plan_de_vol.json ─────► F02 IN/
F02 CASTELLAN OUT/ plan_de_vol.json ────► F03 IN/
F03 SIGISMUND OUT/ video_render.mp4 ────► F04 IN/
F04 INWIT     OUT/ youtube_*.mp4 ───────► Téléchargement opérateur
```

---

## Héritage CRUSADER — Éléments Portés (Coût Déjà Payé)

| Élément | Frégates DORN | Origine CRUSADER | Commentaire |
|---------|---------------|------------------|-------------|
| `calculateMetadata` Remotion | F03 | F03 SIGISMUND | Durée dynamique depuis JSON |
| `--gl swangle` flag | F03 | F03 SIGISMUND | Rendu logiciel Colab |
| Modal chunking 3 workers | F03 | F03/crs_f03_modal_worker.py | Adapté pour plan_de_vol.json |
| Architecture src/ Remotion | F03 | F03 src/ (Root, Main, components) | Composants SVG math vs stickman |
| FFmpeg pipeline F04 | F04B | F04/crs_f04_helbrecht.py | + setpts conditionnel (nouveau V3) |
| `validated_by_magos: true` | F02 | F02 CASTELLAN | Pattern de validation identique |
| `CRS_CUSTOS.py` | Toutes | CRS_CUSTOS.py | Adapté pour frégates DORN |
| IN/ → CODEBASE/ → OUT/ structure | Toutes | Toutes | Architecture identique |

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
| 2026-05-29 | 60 fps fixe (vs 30 fps CRUSADER) | Visualisations mathématiques fluides |
| 2026-05-29 | Streamlit pour F02 (vs Flask CRUSADER) | Canvas JS natif Streamlit |
| 2026-05-29 | Timing dynamique (math → durée) | La courbe dicte la composition |
| 2026-05-29 | step_per_frame calculé par Gemini | Opérateur donne durée cible |
| 2026-06-06 | META_CAMERA absorbé dans META_POLUX V5 | Un seul chat Gemini/Claude — INPUT_5 vidéo référence optionnel |
| 2026-05-29 | F04 scindé F04A + F04B | Viewer de validation avant encoding final |
| 2026-05-29 | playback_speed 1.0 → FFmpeg setpts conditionnel | Skip re-encode si speed=1.0 |
| 2026-05-29 | complexity_coefficient par engine_type | Gemini adapte le rythme |
| 2026-05-29 | Modal chunking hérité de CRUSADER | 17h de débogage économisées |
| 2026-05-29 | CRS_CUSTOS.py adapté (pas réécrit) | Architecture identique, chemins changent |

---

## Fil d'Ariane — Log Chronologique Complet

| Date | Frégate | Phase | Action | Validé |
|------|---------|-------|--------|--------|
| 2026-06-06 | META_POLUX | FORGE | META_POLUX V4 → V5 : ÉTAPE 5 caméra intégrée, 5 inputs | ✓ |
| 2026-06-06 | META_CAMERA | SUPPRESSION | META_CAMERA.md supprimé — absorbé dans META_POLUX V5 | ✓ |
| 2026-06-05 | DORN | SCELLEMENT | PROJET DORN SCELLÉ DANS SON ENTIER | ✓ |
| 2026-06-05 | F04B | PROD | FFmpeg Finishing + contrôle qualité — SCELLÉ | ✓ |
| 2026-06-05 | F04A | PROD | Viewer vitesse + CRS_CUSTOS — SCELLÉ | ✓ |
| 2026-06-05 | F02 | PROD | Test de production complet — SCELLÉ | ✓ |
| 2026-06-05 | F03 | PROD | Test de production complet — SCELLÉ | ✓ |
| 2026-06-05 | F03 | PROD | Bugfix #7 : images PNG/JPEG → public/IN/ | ✓ |
| 2026-05-31 | F01 | PROD | Test de production complet — SCELLÉ | ✓ |
| 2026-05-30 | F04 | AUDIT | Bug 1 : corriger appels CUSTOS F04A/F04B → F04 | ✓ |
| 2026-05-30 | F03 | AUDIT | Bugs 2-5 : MODAL, complexity_coeff, regex, camera | ✓ |
| 2026-05-30 | F02 | AUDIT | Bug 6 : import os DRN_F02.ipynb | ✓ |
| 2026-05-29 | — | INIT | Création repo + structure + Directive V3 | ✓ |

---

## F01 — POLUX ✓ SCELLÉ
- Statut : **SCELLÉ — 2026-05-31** | Test prod : RÉUSSI

## F02 — CASTELLAN ✓ SCELLÉ
- Statut : **SCELLÉ — 2026-06-05** | Test prod : RÉUSSI

## F03 — SIGISMUND ✓ SCELLÉ
- Statut : **SCELLÉ — 2026-06-05** | Test prod : RÉUSSI
- Assets PNG et JPEG supportés depuis `CODEBASE/public/IN/`

## F04A — INWIT ✓ SCELLÉ
- Statut : **SCELLÉ — 2026-06-05** | Test prod : RÉUSSI

## F04B — INWIT ✓ SCELLÉ
- Statut : **SCELLÉ — 2026-06-05** | Test prod : RÉUSSI
- Output : youtube_short.mp4 — 3.50 MB — H.264 — camouflage Lavf58.76.100

## METAPROMPTS
- META_POLUX.md — V5 en cours (5 inputs, camera intégré)
- META_CAMERA.md — **SUPPRIMÉ** — règles absorbées dans META_POLUX V5 ÉTAPE 5

