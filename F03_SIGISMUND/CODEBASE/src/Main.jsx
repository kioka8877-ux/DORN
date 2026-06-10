import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { VirtualCamera }  from "./components/VirtualCamera";
import { CurveTracer }    from "./components/CurveTracer";
import { AssetTracker }   from "./components/AssetTracker";
import { evalMath, computeRevealProgress } from "./components/MathInterpreter";

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
    hud_config = {},
  } = planDeVol;

  const { yMin, yMax, totalFrames } = computed;

  // Facteur d'échelle F02→F03 : F02 canvas = 460px, F03 = height px
  const videoScale = height / 460;

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
        background: hud_config.background_color || "#0a0a0f",
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

          {/* Labels inline — suit le tip de chaque courbe */}
          {reactor_curves.map((curve) => (
            <CurveLabel
              key={`label-${curve.id}`}
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

      {/* ── Titre — screen-space, immunisé caméra ── */}
      <div
        style={{
          position:      "absolute",
          top:           0,
          left:          0,
          right:         0,
          textAlign:     "center",
          paddingTop:    24,
          zIndex:        10,
          fontFamily:    concept_metadata.title_font    || "Impact",
          fontSize:      (concept_metadata.title_size_px || 26) * videoScale,
          color:         concept_metadata.title_color   || "#FFFFFF",
          fontWeight:    "bold",
          letterSpacing: 2,
        }}
      >
        {concept_metadata.title || ""}
      </div>

      {/* ── Thèse — screen-space, bas d'écran ── */}
      {concept_metadata.thesis && (
        <div
          style={{
            position:   "absolute",
            bottom:     24,
            left:       0,
            right:      0,
            textAlign:  "center",
            zIndex:     10,
            fontFamily: concept_metadata.thesis_font    || "Arial",
            fontSize:   (concept_metadata.thesis_size_px || 14) * videoScale,
            color:      concept_metadata.thesis_color   || "#aaaaaa",
            fontWeight: "bold",
            padding:    "0 48px",
          }}
        >
          {concept_metadata.thesis}
        </div>
      )}

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
    const cx   = M.left + plotW / 2;
    const cy   = M.top  + plotH / 2;
    const maxR = Math.min(plotW, plotH) / 2;
    const rings = 5;
    return (
      <>
        <defs>
          <marker id="dorn-axis-arrow" viewBox="0 0 10 10" refX="8" refY="5"
            markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#999999" />
          </marker>
        </defs>
        <g opacity={0.25}>
          {Array.from({ length: rings }, (_, i) => (
            <circle key={i} cx={cx} cy={cy}
              r={(maxR * (i + 1)) / rings}
              fill="none" stroke="#2a2a2a" strokeWidth={1} />
          ))}
          {Array.from({ length: 12 }, (_, i) => {
            const a = (i / 12) * 2 * Math.PI;
            return (
              <line key={i} x1={cx} y1={cy}
                x2={cx + maxR * Math.cos(a)} y2={cy + maxR * Math.sin(a)}
                stroke="#2a2a2a" strokeWidth={1} />
            );
          })}
        </g>
        <line x1={cx - maxR - 12} y1={cy} x2={cx + maxR + 14} y2={cy}
          stroke="#999999" strokeWidth={1.5} markerEnd="url(#dorn-axis-arrow)" />
        <line x1={cx} y1={cy + maxR + 12} x2={cx} y2={cy - maxR - 14}
          stroke="#999999" strokeWidth={1.5} markerEnd="url(#dorn-axis-arrow)" />
      </>
    );
  }

  // Cartésien
  const N = 8;
  const toX = (x) => M.left + ((x - timing.x_range.start) / (timing.x_range.end - timing.x_range.start)) * plotW;
  const toY = (y) => M.top  + ((yMax - y) / (yMax - yMin)) * plotH;

  return (
    <>
      {/* Arrow marker defs */}
      <defs>
        <marker id="dorn-axis-arrow" viewBox="0 0 10 10" refX="8" refY="5"
          markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#999999" />
        </marker>
      </defs>

      {/* Grille de fond — très discrète */}
      <g opacity={0.3}>
        {Array.from({ length: N + 1 }, (_, i) => {
          const x = timing.x_range.start + i * (timing.x_range.end - timing.x_range.start) / N;
          return <line key={`v${i}`} x1={toX(x)} y1={M.top} x2={toX(x)} y2={M.top + plotH}
            stroke="#1a1a1a" strokeWidth={1} />;
        })}
        {Array.from({ length: N + 1 }, (_, i) => {
          const y = yMin + i * (yMax - yMin) / N;
          return <line key={`h${i}`} x1={M.left} y1={toY(y)} x2={M.left + plotW} y2={toY(y)}
            stroke="#1a1a1a" strokeWidth={1} />;
        })}
      </g>

      {/* Labels X — lisibles */}
      {Array.from({ length: N + 1 }, (_, i) => {
        const x = timing.x_range.start + i * (timing.x_range.end - timing.x_range.start) / N;
        return (
          <text key={`lx${i}`} x={toX(x)} y={M.top + plotH + 22}
            fill="#888888" fontSize={13} textAnchor="middle">
            {x.toFixed(1)}
          </text>
        );
      })}

      {/* Labels Y — lisibles */}
      {Array.from({ length: N + 1 }, (_, i) => {
        const y = yMin + i * (yMax - yMin) / N;
        return (
          <text key={`ly${i}`} x={M.left - 8} y={toY(y) + 5}
            fill="#888888" fontSize={12} textAnchor="end">
            {y.toFixed(2)}
          </text>
        );
      })}

      {/* Axe Y — bordure gauche visible avec flèche */}
      <line
        x1={M.left} y1={M.top + plotH + 8}
        x2={M.left} y2={M.top - 16}
        stroke="#999999" strokeWidth={1.5}
        markerEnd="url(#dorn-axis-arrow)"
      />

      {/* Axe X — bordure basse visible avec flèche */}
      <line
        x1={M.left - 8} y1={M.top + plotH}
        x2={M.left + plotW + 16} y2={M.top + plotH}
        stroke="#999999" strokeWidth={1.5}
        markerEnd="url(#dorn-axis-arrow)"
      />

      {/* Croisement y=0 (si dans le range) — tirets discrets */}
      {yMin <= 0 && yMax >= 0 && (
        <line x1={M.left} y1={toY(0)} x2={M.left + plotW} y2={toY(0)}
          stroke="#444444" strokeWidth={1} strokeDasharray="4,4" />
      )}

      {/* Croisement x=0 (si dans le range) — tirets discrets */}
      {timing.x_range.start <= 0 && timing.x_range.end >= 0 && (
        <line x1={toX(0)} y1={M.top} x2={toX(0)} y2={M.top + plotH}
          stroke="#444444" strokeWidth={1} strokeDasharray="4,4" />
      )}
    </>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// CURVELABEL — affiche le nom de l'équation au tip de la courbe
// Apparaît dès les premières frames, suit la tête de tracé
// ─────────────────────────────────────────────────────────────────────────────
const CurveLabel = ({ curve, frame, timing, toCanvasX, toCanvasY, geometryMode }) => {
  const { math_input, render_style, animation_speed, label } = curve;
  const color    = render_style?.color_hex ?? "#00FFFF";
  const revStyle = animation_speed?.reveal_style ?? "linear";
  const pace     = animation_speed?.pace_factor  ?? 1.0;

  const revealFrames =
    (timing.x_range.end - timing.x_range.start) / timing.step_per_frame *
    (timing.complexity_coefficient ?? 1.0);

  const progress = computeRevealProgress(frame, revealFrames, revStyle, pace);
  if (progress < 0.02) return null;

  const xPos = timing.x_range.start + progress * (timing.x_range.end - timing.x_range.start);

  let cx, cy;
  if (geometryMode === "polar") {
    const r = evalMath(math_input, xPos, geometryMode);
    if (r === null) return null;
    cx = toCanvasX(r * Math.cos(xPos));
    cy = toCanvasY(r * Math.sin(xPos));
  } else {
    const y = evalMath(math_input, xPos, geometryMode);
    if (y === null) return null;
    cx = toCanvasX(xPos);
    cy = toCanvasY(y);
  }

  if (!isFinite(cx) || !isFinite(cy)) return null;

  const displayLabel = label || `y = ${math_input}`;

  return (
    <text
      x={cx + 14}
      y={cy - 10}
      fill={render_style?.equation_label_color || color}
      fontSize={render_style?.equation_label_size_px || 15}
      fontFamily={render_style?.equation_label_font || "'Courier New', monospace"}
      fontWeight="bold"
      opacity={0.92}
      filter={`url(#glow-${curve.id})`}
    >
      {displayLabel}
    </text>
  );
};
