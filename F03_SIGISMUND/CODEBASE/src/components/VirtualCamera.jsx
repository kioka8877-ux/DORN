import React from "react";
import { interpolate } from "remotion";
import { evalMath } from "./MathInterpreter";

// ─────────────────────────────────────────────────────────────────────────────
// VirtualCamera — applique les mouvements de caméra du camera_plan
// Modes : follow_asset | static | wide_reveal | push_in | final_proof_lock
// Wrap les enfants dans un div transformé (zoom / pan / shake)
// ─────────────────────────────────────────────────────────────────────────────

// Fonctions d'easing
const EASINGS = {
  easeInOutCubic: (t) =>
    t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2,
  easeInCubic:  (t) => t ** 3,
  easeOutCubic: (t) => 1 - (1 - t) ** 3,
  easeInOutQuad: (t) =>
    t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2,
  linear: (t) => t,
};

export const VirtualCamera = ({
  frame,
  width,
  height,
  cameraPlan,
  reactor_curves,
  timing,
  computed,
  toCanvasX,
  toCanvasY,
  children,
}) => {
  // Pas de camera_plan ou aucun segment → pas de transformation
  if (!cameraPlan?.camera_segments?.length) {
    return (
      <div style={{ width, height, position: "relative" }}>{children}</div>
    );
  }

  const {
    global_style   = {},
    camera_segments,
  } = cameraPlan;

  const shakeIntensity = global_style.shake_intensity ?? 0.08;
  const easingFn       = EASINGS[global_style.default_easing] ?? EASINGS.easeInOutCubic;

  // Segment actif pour ce frame
  const active =
    camera_segments.find((s) => frame >= s.start_frame && frame <= s.end_frame) ??
    camera_segments[camera_segments.length - 1];

  if (!active) {
    return <div style={{ width, height, position: "relative" }}>{children}</div>;
  }

  const {
    start_frame,
    end_frame,
    zoom     = 1.0,
    x_offset = 0,
    y_offset = 0,
    shake    = 0,
    mode     = "static",
  } = active;

  // Progrès interpolé dans le segment
  const t = interpolate(frame, [start_frame, end_frame], [0, 1], {
    extrapolateLeft:  "clamp",
    extrapolateRight: "clamp",
    easing:           easingFn,
  });

  // Zoom interpole : zoom démarre à 1.0 et atteint la valeur cible
  const currentZoom = 1.0 + (zoom - 1.0) * t;

  // Pan interpolé
  const currentX = x_offset * t;
  const currentY = y_offset * t;

  // Shake pseudo-aléatoire (bruit trigonométrique déterministe)
  const shakeX =
    shake > 0
      ? Math.sin(frame * 17.391 + 0.71) * shake * shakeIntensity * 20
      : 0;
  const shakeY =
    shake > 0
      ? Math.cos(frame * 13.731 + 1.23) * shake * shakeIntensity * 12
      : 0;

  // Point de pivot
  let pivotX = width  / 2;
  let pivotY = height / 2;

  if (mode === "follow_asset" && active.target_curve_id) {
    const tc = reactor_curves?.find((c) => c.id === active.target_curve_id);
    if (tc && toCanvasX && toCanvasY) {
      const revealFrames =
        (timing.x_range.end - timing.x_range.start) / timing.step_per_frame;
      const prog = Math.min(frame / revealFrames, 1);
      const xPos = timing.x_range.start + prog * (timing.x_range.end - timing.x_range.start);
      const yVal = evalMath(tc.math_input, xPos);
      if (yVal !== null) {
        pivotX = toCanvasX(xPos);
        pivotY = toCanvasY(yVal);
      }
    }
  }

  // Transformation CSS
  const transform = [
    `translate(${width / 2 + currentX + shakeX}px, ${height / 2 + currentY + shakeY}px)`,
    `scale(${currentZoom})`,
    `translate(${-width / 2}px, ${-height / 2}px)`,
  ].join(" ");

  return (
    <div
      style={{
        width,
        height,
        position:        "relative",
        transformOrigin: `${pivotX.toFixed(1)}px ${pivotY.toFixed(1)}px`,
        transform,
        willChange:      "transform",
      }}
    >
      {children}
    </div>
  );
};
