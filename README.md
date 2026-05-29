# PENTERACT DORN
## Pipeline de Visualisation Mathématique — Pop-Science Culture Algorithmique

> *"Seek perfection of mind, body, and soul."* — Rogal Dorn, VIIe Légion

---

## STATUT DE LA CROISADE

```
[░░░░░░░░░░░░░░░░] STRUCTURE INITIALISÉE — 0/4 FRÉGATES SCELLÉES
```

**Phase active : FORGE**

---

## Présentation

**PENTERACT DORN** est un pipeline de production vidéo automatisé générant des **visualisations mathématiques animées au style Neon SVG** — conçu pour le format Pop-Science Culture sur YouTube Shorts / TikTok.

- **Format** : Vertical 1080×1920 (Shorts) ou Horizontal 1920×1080 (Long-form)
- **Objectif** : Trancher des débats pop-culture (sport, musique, physique) par la géométrie et le code neon
- **Coût** : 0.00 EUR (Colab + Drive + Modal gratuit)
- **FPS** : 60 — timing dynamique (la math dicte la durée)

---

## Philosophie — Le Nouvel Élément

L'idée de PENTERACT DORN naît d'une rupture architecturale : remplacer les mathématiques abstraites froides
par un **Nouvel Élément** à haute densité émotionnelle — la Pop-Science Culture.
Prendre les grands débats iconiques (Messi vs CR7, Kobe vs Jordan, la voix de Sia) et les trancher
de manière irréfutable par la géométrie, la physique et le code neon.

> *L'émotion attire le spectateur. La rigueur mathématique le retient.*

---

## Architecture — Les 4 Frégates

```
META_POLUX (Gemini — chat manuel, 4 inputs)
       │
       ▼
F01_POLUX → plan_de_vol.json (timing calculé, EXIF stripé)
       │
META_CAMERA (Gemini — chat manuel)
       │
       ▼
F02_CASTELLAN → plan_de_vol.json (figé, validated_by_magos)
       │
       ▼
F03_SIGISMUND → video_render.mp4  [Remotion 60fps — SVG neon — timing dynamique]
       │
       ▼
F04A_INWIT → [Viewer + Speed Control — 0.5x → 2x]
       │
       ▼
F04B_INWIT → youtube_short.mp4 / youtube_long.mp4
```

| Frégate | Nom | Rôle |
|---------|-----|------|
| F01 | POLUX | Oracle & Curation — validation JSON + strip EXIF PNG |
| F02 | CASTELLAN | HUD Contrôle — Streamlit + Canvas JS + simulation |
| F03 | SIGISMUND | Réacteur Multi-Formes — Remotion SVG neon 60fps |
| F04A | INWIT | Viewer + Speed Control — Player HTML Colab |
| F04B | INWIT | FFmpeg Finishing — re-encode + wipe + setpts conditionnel |

---

## Framework de Réflexion — ATOM-IC

Toute décision technique est filtrée par ATOM-IC (Atomic Transmutation & Optimized Methods for Industrial Creation) :

| Phase | Framework | Question de référence |
|-------|-----------|----------------------|
| [A] Analyse Subatomique | First Principles | Quel est l'atome de donnée minimal ? |
| [T] Transmutation Inventive | TRIZ | Quelle contradiction peut être retournée en avantage ? |
| [O] Optimisation Cinétique | Pareto 95/5 | Quels 5% d'effort produisent 95% d'impact visuel ? |
| [M] Manifestation N.U.K.E | N.U.K.E | Comment s'exécute en 1 commande headless, sans clic ? |

---

## Pile Technologique

| Outil | Rôle | Frégate |
|-------|------|---------|
| math.js (CDN) | Évaluation expressions mathématiques | F02, F03 |
| Remotion 4.x | React → vidéo 60fps | F03 |
| Streamlit | HUD contrôle + simulation | F02 |
| Modal serverless | Chunking parallèle 3 workers | F03 |
| FFmpeg | Assemblage + camouflage | F04B |
| Google Colab | Environnement d'exécution | Toutes |
| Google Drive | Stockage inter-frégates | Toutes |

---

## Héritage CRUSADER

PENTERACT DORN hérite des patterns techniques validés en production dans CRUSADER
(17h de débogage économisées — coût déjà payé) :

| Pattern hérité | Frégates PENTERACT DORN | Source CRUSADER |
|----------------|---------------|-----------------|
| `calculateMetadata` Remotion (durée depuis JSON) | F03 | F03 SIGISMUND |
| `--gl swangle` flag (rendu logiciel Colab) | F03 | F03 SIGISMUND |
| Modal chunking parallèle 3 workers | F03 | F03 SIGISMUND |
| FFmpeg : `-map_metadata -1` + CRF18 + `+faststart` + loudnorm | F04B | F04 HELBRECHT |
| `validated_by_magos: true` (clé de validation JSON) | F02 | F02 CASTELLAN |
| `CRS_CUSTOS.py` (validation check-in / check-out) | Toutes | Toutes |
| Architecture frégates étanches (IN/ → CODEBASE/ → OUT/) | Toutes | Toutes |

---

## Axiomes du Projet

1. **Gratuit** — Zéro API payante, zéro dépendance cloud commerciale
2. **60 fps** — Standard PENTERACT DORN (timing dynamique — la math dicte la durée)
3. **Timing dynamique** — `calculateMetadata` Remotion lit le JSON, coupe parfaite zéro manipulation
4. **Colab-first** — Tout tourne dans Colab, le PC est une télécommande
5. **Isolation des frégates** — Chaque frégate opère en silo : IN/ → CODEBASE/ → OUT/
6. **Transfert validé** — Tout transit inter-frégate passe par `CRS_CUSTOS.py` (check-out + check-in)
7. **Budget zéro** — 0.00 EUR, toujours, sans exception

---

## Gardien de Flotte

```bash
python CRS_CUSTOS.py --frigate F01 --mode check-out --drive-base /content/drive/MyDrive/DRIVE_DORN
python CRS_CUSTOS.py --frigate F02 --mode check-in  --drive-base /content/drive/MyDrive/DRIVE_DORN
```

---

## Structure du Repo

```
DORN/
├── README.md
├── CRS_CUSTOS.py                       ← Adapté de CRUSADER (frégates DORN)
├── DORN_V3_DIRECTIVE_IMPERIALE.pdf     ← Document de référence scellé
├── TRACKING/
│   ├── DORN_CAMPAIGN_LOG.md            ← Carnet de bord + décisions de forge
│   └── DORN_TRANSFER_LOG.md            ← Schémas JSON + registre transferts
├── METAPROMPTS/
│   ├── META_POLUX.md                   ← À sceller (Phase Forge)
│   └── META_CAMERA.md                  ← À sceller (Phase Forge)
├── SHARED/
│   ├── IN/
│   └── OUT/
├── F01_POLUX/
│   ├── IN/
│   ├── OUT/
│   └── CODEBASE/
├── F02_CASTELLAN/
│   ├── IN/
│   ├── OUT/
│   └── CODEBASE/
├── F03_SIGISMUND/
│   ├── IN/
│   ├── OUT/
│   └── CODEBASE/
└── F04_INWIT/
    ├── IN/
    ├── OUT/
    └── CODEBASE/
```

---

## Document de Référence

`DORN_V3_DIRECTIVE_IMPERIALE.pdf` à la racine du repo — contient l'architecture complète,
les schémas JSON, le détail de chaque frégate, et le framework ATOM-IC.

---

*Nomenclature tirée du lore Warhammer 40K — VIIe Légion des Imperial Fists.*
