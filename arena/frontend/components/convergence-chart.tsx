export interface ConvergenceChartProps {
  genLog: [number, number, number][]; // [gen, best, avg]
  optimal: number;
  upToGen: number; // frame index into genLog (inclusive)
  size?: number;
}

export function ConvergenceChart({ genLog, optimal, upToGen, size = 480 }: ConvergenceChartProps) {
  const pad = 40;
  const w = size;
  const h = Math.round(size * 0.6);
  const gens = genLog.map((g) => g[0]);
  const minGen = gens[0] ?? 0;
  const maxGen = gens[gens.length - 1] ?? 1;
  const spanGen = maxGen - minGen || 1;
  const allVals = genLog.flatMap((g) => [g[1], g[2]]);
  const maxVal = Math.max(...allVals, optimal);
  const minVal = Math.min(...allVals, optimal);
  const yLo = minVal - (maxVal - minVal) * 0.05;
  const yHi = maxVal + (maxVal - minVal) * 0.05;
  const spanY = yHi - yLo || 1;

  const sx = (gen: number) => pad + ((gen - minGen) / spanGen) * (w - 2 * pad);
  const sy = (v: number) => pad + (1 - (v - yLo) / spanY) * (h - 2 * pad);

  const upto = Math.max(0, Math.min(upToGen, genLog.length - 1));
  const slice = genLog.slice(0, upto + 1);
  const pointsFor = (idx: 1 | 2) => slice.map((g) => `${sx(g[0]).toFixed(1)},${sy(g[idx]).toFixed(1)}`).join(" ");
  const yOpt = sy(optimal);
  const current = genLog[upto];

  return (
    <svg
      viewBox={`0 0 ${w} ${h}`}
      width="100%"
      role="img"
      aria-label="yakınsama grafiği"
      data-testid="convergence-chart"
      className="w-full rounded-lg border border-border/70 bg-card text-primary shadow-sm"
    >
      <rect x={pad} y={pad} width={w - 2 * pad} height={h - 2 * pad} fill="none" stroke="currentColor" strokeOpacity="0.18" strokeWidth="1" rx="6" />
      <line data-testid="optimal-line" x1={pad} y1={yOpt} x2={w - pad} y2={yOpt} stroke="currentColor" strokeOpacity="0.4" strokeWidth="1" strokeDasharray="4 4" />
      <text x={w - pad} y={yOpt - 4} textAnchor="end" className="fill-muted-foreground text-[10px]">optimum {optimal}</text>
      <polyline data-testid="avg-curve" points={pointsFor(2)} fill="none" stroke="currentColor" strokeOpacity="0.35" strokeWidth="1.5" />
      <polyline data-testid="best-curve" points={pointsFor(1)} fill="none" stroke="currentColor" strokeWidth="2" />
      {current && (
        <text x={pad} y={pad - 12} className="fill-foreground text-[11px]">
          nesil {current[0]} · en iyi {current[1]} · ort. {Math.round(current[2])}
        </text>
      )}
    </svg>
  );
}
