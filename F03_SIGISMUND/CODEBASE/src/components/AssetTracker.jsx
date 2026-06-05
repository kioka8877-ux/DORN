import React from "react";
import { staticFile } from "remotion";
import { evalMath, computeRevealProgress, computeSlope } from "./MathInterpreter";

// ─────────────────────────────────────────────────────────────────────────────
// AssetTracker — suit une image PNG/JPEG le long d'une courbe
// Rotation automatique selon la pente (auto_rotate_slope)
// Inertia smoothing : amortit légèrement la position (inertia_smooth)
// Le fichier (PNG ou JPEG) doit être accessible depuis src/public/IN/<asset_filename>
// ─────────────────────────────────────────────────────────────────────────────
export const AssetTracker = ({
  curve,
  frame,
  timing,
  toCanvasX,
  toCanvasY,
  geometryMode,
}) => {
  const { math_input, animation_speed, tracking_target } = curve;
  if (!tracking_target?.asset_filename) return null;

  const {
    asset_filename,
    scale_factor = 1.0,
    physics      = {},
  } = tracking_target;

  const auto_rotate_slope = physics.auto_rotate_slope ?? true;
  const inertia_smooth    = Math.max(0, Math.min(0.9, physics.inertia_smooth ?? 0.1));

  const revStyle = animation_speed?.reveal_style ?? "linear";
  const pace     = animation_speed?.pace_factor  ?? 1.0;

  const revealFrames =
    (timing.x_range.end - timing.x_range.start) / timing.step_per_frame *
    (timing.complexity_coefficient ?? 1.0);

  // Progrès de l'animation
  const progress = computeRevealProgress(frame, revealFrames, revStyle, pace);

  // Inertia : l'asset est légèrement en retard sur la tête de courbe
  // On simule en décalant le progrès de quelques frames
  const inertiaDelay = inertia_smooth * 15; // frames de retard max
  const delayedFrame = Math.max(0, frame - inertiaDelay);
  const delayedProgress = computeRevealProgress(delayedFrame, revealFrames, revStyle, pace);

  const xTracked = timing.x_range.start + delayedProgress * (timing.x_range.end - timing.x_range.start);
  const y = evalMath(math_input, xTracked, geometryMode);
  if (y === null) return null;

  let cx, cy;
  if (geometryMode === "polar") {
    const r     = y;
    const theta = xTracked;
    cx = toCanvasX(r * Math.cos(theta));
    cy = toCanvasY(r * Math.sin(theta));
  } else {
    cx = toCanvasX(xTracked);
    cy = toCanvasY(y);
  }

  if (!isFinite(cx) || !isFinite(cy)) return null;

  // Rotation selon la pente
  let rotateDeg = 0;
  if (auto_rotate_slope && geometryMode === "cartesian") {
    const slope  = computeSlope(math_input, xTracked);
    rotateDeg    = (Math.atan(slope) * 180) / Math.PI;
  }

  const size = 80 * scale_factor;

  // staticFile() resout correctement le chemin en dev ET en rendu headless.
  // Supporte PNG et JPEG (asset_filename = "image.png" ou "image.jpg"/".jpeg").
  // Le notebook copie les images de IN/ → CODEBASE/public/IN/ avant le rendu.
  const src = staticFile(`IN/${asset_filename}`);

  return (
    <g transform={`translate(${cx.toFixed(1)}, ${cy.toFixed(1)}) rotate(${rotateDeg.toFixed(2)})`}>
      <image
        href={src}
        x={-size / 2}
        y={-size / 2}
        width={size}
        height={size}
        preserveAspectRatio="xMidYMid meet"
      />
    </g>
  );
};
