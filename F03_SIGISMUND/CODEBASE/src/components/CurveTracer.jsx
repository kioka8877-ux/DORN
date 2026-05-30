import React, { useMemo } from "react";
import { evalMath, computeRevealProgress } from "./MathInterpreter";

// ─────────────────────────────────────────────────────────────────────────────
// CurveTracer — dessine une courbe SVG neon progressivement
// Supporte cartesian et polar
// Effets : glow layeré (SVG filter), dot tip animé, discontinuités gérées
// ─────────────────────────────────────────────────────────────────────────────
export const CurveTracer = ({
  curve,
  frame,
  timing,
  toCanvasX,
  toCanvasY,
  geometryMode,
}) => {
  const { id, math_input, render_style, animation_speed } = curve;
  const color     = render_style?.color_hex      ?? "#00FFFF";
  const glowR     = render_style?.glow_radius_px ?? 20;
  const lineW     = render_style?.line_width_px  ?? 6;
  const revStyle  = animation_speed?.reveal_style ?? "linear";
  const pace      = animation_speed?.pace_factor  ?? 1.0;

  // Frames total pour révéler toute la courbe
  const revealFrames =
    (timing.x_range.end - timing.x_range.start) / timing.step_per_frame;

  const progress  = computeRevealProgress(frame, revealFrames, revStyle, pace);
  const xCurrent  = timing.x_range.start + progress * (timing.x_range.end - timing.x_range.start);

  // Résolution adaptative : plus de points quand la courbe est complexe
  const RESOLUTION = 800;

  const { pathData, tipX, tipY } = useMemo(() => {
    const xStart = timing.x_range.start;
    const xEnd   = xCurrent;

    if (xEnd <= xStart || progress <= 0) return { pathData: "", tipX: null, tipY: null };

    const steps = Math.max(Math.ceil(RESOLUTION * Math.max(progress, 0.01)), 2);
    const dx    = (xEnd - xStart) / steps;
    const pts   = [];

    for (let i = 0; i <= steps; i++) {
      const x = xStart + i * dx;
      const y = evalMath(math_input, x, geometryMode);
      if (y === null) continue;

      let cx, cy;
      if (geometryMode === "polar") {
        // f(theta) = r  →  x_cart = r*cos(theta), y_cart = r*sin(theta)
        const theta = x;
        const r     = y;
        cx = toCanvasX(r * Math.cos(theta));
        cy = toCanvasY(r * Math.sin(theta));
      } else {
        cx = toCanvasX(x);
        cy = toCanvasY(y);
      }

      if (isFinite(cx) && isFinite(cy)) pts.push({ x: cx, y: cy });
    }

    if (pts.length === 0) return { pathData: "", tipX: null, tipY: null };

    // Construction du path SVG avec détection de discontinuités
    const JUMP_THRESHOLD = 250; // px
    let d = `M ${pts[0].x.toFixed(1)} ${pts[0].y.toFixed(1)}`;
    for (let i = 1; i < pts.length; i++) {
      const dist = Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y);
      if (dist > JUMP_THRESHOLD) {
        d += ` M ${pts[i].x.toFixed(1)} ${pts[i].y.toFixed(1)}`;
      } else {
        d += ` L ${pts[i].x.toFixed(1)} ${pts[i].y.toFixed(1)}`;
      }
    }

    const last = pts[pts.length - 1];
    return { pathData: d, tipX: last.x, tipY: last.y };
  }, [frame, math_input, timing, geometryMode, xCurrent, progress]);

  if (!pathData) return null;

  return (
    <g>
      {/* Halo large (glow extérieur) */}
      <path
        d={pathData}
        fill="none"
        stroke={color}
        strokeWidth={lineW * 4}
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity={0.15}
        filter={`url(#glow-${id})`}
      />

      {/* Halo intermédiaire */}
      <path
        d={pathData}
        fill="none"
        stroke={color}
        strokeWidth={lineW * 2}
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity={0.35}
        filter={`url(#glow-${id})`}
      />

      {/* Ligne principale */}
      <path
        d={pathData}
        fill="none"
        stroke={color}
        strokeWidth={lineW}
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity={0.95}
      />

      {/* Dot tip (visible tant que la courbe n'est pas complète) */}
      {progress < 0.999 && tipX !== null && (
        <>
          <circle cx={tipX} cy={tipY} r={lineW * 2.5} fill={color} opacity={0.25} />
          <circle cx={tipX} cy={tipY} r={lineW * 1.4} fill={color} opacity={0.9} />
        </>
      )}
    </g>
  );
};
