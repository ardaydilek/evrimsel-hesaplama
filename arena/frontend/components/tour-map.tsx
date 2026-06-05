export interface TourMapProps {
  coordinates: [number, number][];
  tour: number[]; // 1-based city ids
  size?: number;
  /** 0..1 — when set, the tour polyline draws in progressively. Omitted/≥1 => full static tour. */
  progress?: number;
}

export function TourMap({ coordinates, tour, size = 480, progress }: TourMapProps) {
  const pad = 36;
  const xs = coordinates.map((c) => c[0]);
  const ys = coordinates.map((c) => c[1]);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const spanX = maxX - minX || 1, spanY = maxY - minY || 1;
  const sx = (x: number) => pad + ((x - minX) / spanX) * (size - 2 * pad);
  const sy = (y: number) => pad + ((maxY - y) / spanY) * (size - 2 * pad); // flip y for screen

  const pts = tour.map((id) => coordinates[id - 1]).filter(Boolean) as [number, number][];
  // NOTE: the test asserts this exact shape — "M ..." + " L ..." per hop + " Z".
  const d = pts.length
    ? "M " + pts.map((p) => `${sx(p[0]).toFixed(1)} ${sy(p[1]).toFixed(1)}`).join(" L ") + " Z"
    : "";

  const start = pts[0];
  // Evenly spaced grid guides (decorative; not <circle> so the city count holds).
  const guides = [0.25, 0.5, 0.75];

  const drawingIn = progress !== undefined && progress < 1;
  const dashProps = progress !== undefined
    ? { pathLength: 1, strokeDasharray: 1, strokeDashoffset: Math.max(0, 1 - progress) }
    : {};

  return (
    <svg
      viewBox={`0 0 ${size} ${size}`}
      width="100%"
      role="img"
      aria-label="tur haritası"
      data-testid="tour-map"
      className="aspect-square w-full max-w-lg rounded-lg border border-border/70 bg-card text-primary shadow-sm"
    >
      <defs>
        <linearGradient id="tour-stroke" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="currentColor" stopOpacity="0.55" />
          <stop offset="100%" stopColor="currentColor" stopOpacity="1" />
        </linearGradient>
        <radialGradient id="tour-node" cx="0.35" cy="0.35" r="0.7">
          <stop offset="0%" stopColor="var(--card)" />
          <stop offset="100%" stopColor="currentColor" />
        </radialGradient>
      </defs>

      {/* Plotting grid */}
      <g stroke="currentColor" strokeOpacity="0.08" strokeWidth="1">
        {guides.map((g) => (
          <line key={`v${g}`} x1={pad + g * (size - 2 * pad)} y1={pad} x2={pad + g * (size - 2 * pad)} y2={size - pad} />
        ))}
        {guides.map((g) => (
          <line key={`h${g}`} x1={pad} y1={pad + g * (size - 2 * pad)} x2={size - pad} y2={pad + g * (size - 2 * pad)} />
        ))}
      </g>
      {/* Plot frame */}
      <rect
        x={pad}
        y={pad}
        width={size - 2 * pad}
        height={size - 2 * pad}
        fill="none"
        stroke="currentColor"
        strokeOpacity="0.18"
        strokeWidth="1"
        rx="6"
      />

      {/* Soft underlay of the trace for depth */}
      {d && !drawingIn && (
        <path d={d} fill="currentColor" fillOpacity="0.05" stroke="none" />
      )}

      {/* The tour itself */}
      {d && (
        <path
          d={d}
          fill="none"
          stroke="url(#tour-stroke)"
          strokeWidth={2}
          strokeLinejoin="round"
          strokeLinecap="round"
          data-testid="tour-path"
          {...dashProps}
        />
      )}

      {/* One node per city (count must equal coordinates.length) */}
      {coordinates.map((c, i) => (
        <circle
          key={i}
          cx={sx(c[0])}
          cy={sy(c[1])}
          r={3.5}
          fill="url(#tour-node)"
          stroke="currentColor"
          strokeWidth="1"
          strokeOpacity="0.9"
        />
      ))}

      {/* Start marker — a square ring, drawn with <rect> so it doesn't inflate
          the city circle count the test relies on. */}
      {start && (
        <rect
          x={sx(start[0]) - 6.5}
          y={sy(start[1]) - 6.5}
          width="13"
          height="13"
          rx="2"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
        />
      )}
    </svg>
  );
}
