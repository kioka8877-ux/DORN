import { evaluate } from "mathjs";

// ─────────────────────────────────────────────────────────────────────────────
// evalMath — évalue une expression math.js pour un x donné
// Retourne null si invalide ou infini
// ─────────────────────────────────────────────────────────────────────────────
export const evalMath = (mathInput, x, geometryMode = "cartesian") => {
  try {
    const raw = evaluate(mathInput, { x, t: x });
    if (!isFinite(raw) || typeof raw !== "number") return null;
    return raw;
  } catch (_) {
    return null;
  }
};

// ─────────────────────────────────────────────────────────────────────────────
// computeRevealProgress — progrès d'animation [0..1] selon reveal_style
// frame          : frame courante
// revealFrames   : nombre total de frames pour révéler toute la courbe
// revealStyle    : "linear" | "ease_in" | "ease_out" | "dramatic"
// paceFactor     : multiplicateur de vitesse (1.0 = normal)
// ─────────────────────────────────────────────────────────────────────────────
export const computeRevealProgress = (
  frame,
  revealFrames,
  revealStyle = "linear",
  paceFactor  = 1.0
) => {
  const raw = Math.min(frame / (revealFrames / paceFactor), 1.0);

  switch (revealStyle) {
    case "ease_in":
      return raw * raw;

    case "ease_out":
      return 1.0 - (1.0 - raw) * (1.0 - raw);

    case "dramatic":
      // Démarrage très lent (<40%), puis accélération soudaine
      if (raw < 0.4) return raw * raw * 0.6;
      return 0.096 + (raw - 0.4) * 1.507;

    case "linear":
    default:
      return raw;
  }
};

// ─────────────────────────────────────────────────────────────────────────────
// computeSlope — pente numérique en x (pour rotation auto des assets)
// ─────────────────────────────────────────────────────────────────────────────
export const computeSlope = (mathInput, x, dx = 0.005, geometryMode = "cartesian") => {
  const y1 = evalMath(mathInput, x - dx, geometryMode);
  const y2 = evalMath(mathInput, x + dx, geometryMode);
  if (y1 === null || y2 === null) return 0;
  const slope = (y2 - y1) / (2 * dx);
  return isFinite(slope) ? slope : 0;
};
