import React from "react";
import { Composition } from "remotion";
import { evaluate } from "mathjs";
import { Main } from "./Main";

// ─────────────────────────────────────────────────────────────────────────────
// calculateMetadata — Axiome DORN V3 : la math dicte la durée
// Reçoit planDeVol depuis --props (CLI Colab/Modal) ou defaultProps (studio)
// ─────────────────────────────────────────────────────────────────────────────
const calculateMetadata = async ({ props }) => {
  const { planDeVol } = props;
  const { timing, concept_metadata, reactor_curves, space_environment } = planDeVol;

  // Durée dynamique
  const revealFrames =
    (timing.x_range.end - timing.x_range.start) / timing.step_per_frame;
  const totalFrames =
    Math.ceil(revealFrames * (timing.complexity_coefficient ?? 1.0)) +
    (timing.final_freeze_frames ?? 180);

  const fps = timing.fps ?? 60;
  const isVertical = concept_metadata.format === "vertical";
  const width  = isVertical ? 1080 : 1920;
  const height = isVertical ? 1920 : 1080;

  // Pre-calcul du range Y pour le coordinate mapping
  const xStart  = timing.x_range.start;
  const xEnd    = timing.x_range.end;
  const samples = 400;
  const step    = (xEnd - xStart) / samples;
  let yMin = Infinity, yMax = -Infinity;

  for (const curve of reactor_curves) {
    for (let i = 0; i <= samples; i++) {
      const x = xStart + i * step;
      try {
        let y;
        if (space_environment.geometry_mode === "polar") {
          const r = evaluate(curve.math_input, { x, t: x });
          y = r * Math.sin(x); // projection Y
        } else {
          y = evaluate(curve.math_input, { x, t: x });
        }
        if (isFinite(y)) {
          if (y < yMin) yMin = y;
          if (y > yMax) yMax = y;
        }
      } catch (_) {
        // expression invalide — on ignore
      }
    }
  }

  // Padding 10% + fallback si toutes les valeurs sont identiques
  const range   = Math.abs(yMax - yMin) || 2.0;
  const padding = range * 0.12;
  const computed = {
    yMin:        yMin === Infinity  ? -2 : yMin - padding,
    yMax:        yMax === -Infinity ?  2 : yMax + padding,
    totalFrames,
  };

  return {
    durationInFrames: totalFrames,
    fps,
    width,
    height,
    props: { ...props, computed },
  };
};

// ─────────────────────────────────────────────────────────────────────────────
// defaultProps — placeholder studio (écrasé par --props au render Colab)
// ─────────────────────────────────────────────────────────────────────────────
const DEFAULT_PLAN = {
  concept_metadata: {
    title:       "DORN — Visualisation",
    hook:        "La courbe révèle la vérité.",
    thesis:      "f(x) = sin(x) · e^(-x/10)",
    engine_type: "time_evolution_comparison",
    format:      "vertical",
    fps:         60,
  },
  timing: {
    fps:                    60,
    target_duration_seconds: 30,
    x_range:                { start: 0, end: 20 },
    step_per_frame:         0.05,
    complexity_coefficient: 1.0,
    final_freeze_frames:    180,
    playback_speed:         1.0,
  },
  space_environment: {
    geometry_mode:    "cartesian",
    x_label:          "x",
    y_label:          "f(x)",
    background_asset: null,
  },
  reactor_curves: [
    {
      id:          "c1",
      math_input:  "sin(x) * exp(-x / 10)",
      render_style: {
        color_hex:      "#00FFFF",
        glow_radius_px: 20,
        line_width_px:  6,
      },
      animation_speed: {
        reveal_style: "ease_out",
        pace_factor:  1.0,
      },
      tracking_target: null,
    },
  ],
  final_frame: {
    annotation:           "Q.E.D.",
    freeze_duration_frames: 90,
  },
  camera_plan: {
    global_style: {
      movement_energy:   "calm",
      default_easing:    "easeInOutCubic",
      shake_intensity:   0.08,
    },
    camera_segments: [],
  },
  audio_synthesizer: {
    wave_type:            "sine",
    base_frequency_hz:    220,
    frequency_multiplier: 12.0,
  },
};

export const Root = () => (
  <Composition
    id="Main"
    component={Main}
    durationInFrames={1380}
    fps={60}
    width={1080}
    height={1920}
    calculateMetadata={calculateMetadata}
    defaultProps={{
      planDeVol: DEFAULT_PLAN,
      computed:  { yMin: -1.2, yMax: 1.2, totalFrames: 1380 },
    }}
  />
);
