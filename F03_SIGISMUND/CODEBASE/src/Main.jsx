import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { VirtualCamera }  from "./components/VirtualCamera";
import { CurveTracer }    from "./components/CurveTracer";
import { AssetTracker }   from "./components/AssetTracker";

// ─────────────────────────────────────────────────────────────────────────────
// MAIN — Composition Remotion principale
// Orchestre : background → grille → courbes → assets → caméra → annotation
// ─────────────────────────────────────────────────────────────────────────────
export const Main = ({ planDeVol, computed }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const {
    timing,
    space_environment,
    reactor_curves,
    final_frame,
    camera_plan,
    concept_metadata,
  } = planDeVol;

  const { yMin, yMax, totalFrames } = computed;

  // Frames de reveal total (sans freeze)
  const revealFrames =
    (timing.x_range.end - timing.x_range.start) / timing.step_per_frame *
    (timing.complexity_coefficient ?? 1.0);

  // Marges du plot
  const M = { top: 90, bottom: 70, left: 70, right: 40 };
  const plotW = width  - M.left - M.right;
  const plotH = height - M.top  - M.bottom;

  // Fonctions de mapping coordonnées math → canvas
  const toCanvasX = (x) =>
    M.left + ((x - timing.x_range.start) / (timing.x_range.end - timing.x_range.start)) * plotW;
  const toCanvasY = (y) =>
    M.top  + ((yMax - y) / (yMax - yMin)) * plotH;

  // Opacité de l'annotation finale
  const freezeStart = Math.ceil(revealFrames);
  const annotOpacity =
    frame >= freezeStart
      ? interpolate(frame, [freezeStart, freezeStart + 25], [0, 1], { extrapolateRight: "clamp" })
      : 0;

  return (
    <div
      style={{
        width, height,
        background: "#000000",
        position:   "relative",
        overflow:   "hidden",
        fontFamily: "'Courier New', monospace",
      }}
    >
      {/* ── Scène SVG (courbes + grille + labels) ── */}
      <VirtualCamera
        frame={frame}
        width={width}
        height={height}
        cameraPlan={camera_plan}
        reactor_curves={reactor_curves}
        timing={timing}
        computed={computed}
        toCanvasX={toCanvasX}
        toCanvasY={toCanvasY}
      >
        <svg
          width={width}
          height={height}
          style={{ position: "absolute", top: 0, left: 0 }}
        >
          <Defs curves={reactor_curves} />

          {/* Grille + axes */}
          <Grid
            M={M} plotW={plotW} plotH={plotH}
            timing={timing} yMin={yMin} yMax={yMax}
            geometryMode={space_environment.geometry_mode}
            width={width} height={height}
          />

          {/* Labels axes */}
          <text
            x={M.left + plotW / 2} y={height - 12}
            fill="#555" fontSize={18} textAnchor="middle"
          >
            {space_environment.x_label || "x"}
          </text>
          <text
            x={18} y={M.top + plotH / 2}
            fill="#555" fontSize={18} textAnchor="middle"
            transform={`rotate(-90, 18, ${M.top + plotH / 2})`}
          >
            {space_environment.y_label || "y"}
          </text>

          {/* Titre */}
          <text
            x={width / 2} y={48}
            fill="#FFFFFF" fontSize={26} textAnchor="middle"
            fontWeight="bold" letterSpacing={2}
          >
            {concept_metadata.title || ""}
          </text>

          {/* Courbes */}
          {reactor_curves.map((curve) => (
            <CurveTracer
              key={curve.id}
              curve={curve}
              frame={frame}
              timing={timing}
              toCanvasX={toCanvasX}
              toCanvasY={toCanvasY}
              geometryMode={space_environment.geometry_mode}
            />
          ))}

          {/* Trackers d'assets */}
          {reactor_curves
            .filter((c) => c.tracking_target?.asset_filename)
            .map((curve) => (
              <AssetTracker
                key={`tracker-${curve.id}`}
                curve={curve}
                frame={frame}
                timing={timing}
                toCanvasX={toCanvasX}
                toCanvasY={toCanvasY}
                geometryMode={space_environment.geometry_mode}
              />
            ))}
        </svg>
      </VirtualCamera>

      {/* ── Annotation frame finale (doré) ── */}
      {annotOpacity > 0 && (
        <div
          style={{
            position:  "absolute",
            bottom:    130,
            left:      0,
            right:     0,
            opacity:   annotOpacity,
            textAlign: "center",
            padding:   "0 48px",
          }}
        >
          <div
            style={{
              display:      "inline-block",
              background:   "rgba(0,0,0,0.85)",
              border:       "2px solid #FFD700",
              borderRadius: 10,
              padding:      "18px 36px",
              color:        "#FFD700",
              fontSize:     34,
              fontWeight:   "bold",
              letterSpacing: 3,
            }}
          >
            {final_frame?.annotation || "Q.E.D."}
          </div>
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// DEFS — filtres SVG glow par courbe
// ─────────────────────────────────────────────────────────────────────────────
const Defs = ({ curves }) => (
  <defs>
    {curves.map((c) => {
      const blur = (c.render_style?.glow_radius_px ?? 20) / 5;
      return (
        <filter
          key={`glow-${c.id}`}
          id={`glow-${c.id}`}
          x="-60%" y="-60%" width="220%" height="220%"
        >
          <feGaussianBlur stdDeviation={blur} result="blur1" />
          <feGaussianBlur stdDeviation={blur * 2} result="blur2" />
          <feMerge>
            <feMergeNode in="blur2" />
            <feMergeNode in="blur1" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      );
    })}
  </defs>
);

// ─────────────────────────────────────────────────────────────────────────────
// GRID — Grille cartésienne ou polaire
// ─────────────────────────────────────────────────────────────────────────────
const Grid = ({ M, plotW, plotH, timing, yMin, yMax, geometryMode, width, height }) => {
  if (geometryMode === "polar") {
    const cx  = M.left + plotW / 2;
    const cy  = M.top  + plotH / 2;
    const maxR = Math.min(plotW, plotH) / 2;
    const rings = 5;
    return (
      <g opacity={0.22}>
        {Array.from({ length: rings }, (_, i) => (
          <circle
            key={i} cx={cx} cy={cy}
            r={(maxR * (i + 1)) / rings}
            fill="none" stroke="#2a2a2a" strokeWidth={1}
          />
        ))}
        {Array.from({ length: 12 }, (_, i) => {
          const a = (i / 12) * 2 * Math.PI;
          return (
            <line
              key={i} x1={cx} y1={cy}
              x2={cx + maxR * Math.cos(a)} y2={cy + maxR * Math.sin(a)}
              stroke="#2a2a2a" strokeWidth={1}
            />
          );
        })}
        <line x1={cx - maxR} y1={cy} x2={cx + maxR} y2={cy} stroke="#444" strokeWidth={1.5} />
        <line x1={cx} y1={cy - maxR} x2={cx} y2={cy + maxR} stroke="#444" strokeWidth={1.5} />
      </g>
    );
  }

  // Cartésien
  const N = 8;
  const toX = (x) => M.left + ((x - timing.x_range.start) / (timing.x_range.end - timing.x_range.start)) * plotW;
  const toY = (y) => M.top  + ((yMax - y) / (yMax - yMin)) * plotH;

  return (
    <g opacity={0.28}>
      {/* Lignes verticales */}
      {Array.from({ length: N + 1 }, (_, i) => {
        const x = timing.x_range.start + i * (timing.x_range.end - timing.x_range.start) / N;
        return (
          <g key={`v${i}`}>
            <line x1={toX(x)} y1={M.top} x2={toX(x)} y2={M.top + plotH} stroke="#1e1e1e" strokeWidth={1} />
            <text x={toX(x)} y={M.top + plotH + 22} fill="#383838" fontSize={14} textAnchor="middle">
              {x.toFixed(1)}
            </text>
          </g>
        );
      })}

      {/* Lignes horizontales */}
      {Array.from({ length: N + 1 }, (_, i) => {
        const y = yMin + i * (yMax - yMin) / N;
        return (
          <g key={`h${i}`}>
            <line x1={M.left} y1={toY(y)} x2={M.left + plotW} y2={toY(y)} stroke="#1e1e1e" strokeWidth={1} />
            <text x={M.left - 6} y={toY(y) + 5} fill="#383838" fontSize={13} textAnchor="end">
              {y.toFixed(2)}
            </text>
          </g>
        );
      })}

      {/* Axe X (y=0) */}
      {yMin <= 0 && yMax >= 0 && (
        <line x1={M.left} y1={toY(0)} x2={M.left + plotW} y2={toY(0)} stroke="#3a3a3a" strokeWidth={1.5} />
      )}

      {/* Axe Y (x=0) */}
      {timing.x_range.start <= 0 && timing.x_range.end >= 0 && (
        <line x1={toX(0)} y1={M.top} x2={toX(0)} y2={M.top + plotH} stroke="#3a3a3a" strokeWidth={1.5} />
      )}
    </g>
  );
};
