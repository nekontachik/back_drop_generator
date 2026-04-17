"use client";

import type { BpmVisualization } from "@/lib/types";

interface BpmChartProps {
  visualization: BpmVisualization;
}

export function BpmChart({ visualization }: BpmChartProps) {
  const { onset_times, onset_values, beat_times } = visualization;

  if (!onset_times.length || !onset_values.length) {
    return (
      <p className="font-mono text-[11px] text-text-dim">
        no visualization data
      </p>
    );
  }

  const WIDTH = 800;
  const HEIGHT = 200;
  const PADDING_TOP = 20;
  const CHART_HEIGHT = 160;

  const maxTime = Math.max(...onset_times);
  const maxValue = Math.max(...onset_values) || 1;

  const toX = (t: number) => (t / maxTime) * WIDTH;
  const toY = (v: number) =>
    HEIGHT - PADDING_TOP - (v / maxValue) * CHART_HEIGHT;

  const polylinePoints = onset_times
    .map((t, i) => `${toX(t).toFixed(1)},${toY(onset_values[i]).toFixed(1)}`)
    .join(" ");

  const firstX = toX(onset_times[0]).toFixed(1);
  const lastX = toX(onset_times[onset_times.length - 1]).toFixed(1);
  const baseline = (HEIGHT - PADDING_TOP).toFixed(1);
  const fillPoints = `${firstX},${baseline} ${polylinePoints} ${lastX},${baseline}`;

  function interpolateValue(time: number): number {
    if (!onset_times.length) return 0;
    let lo = 0;
    for (let i = 0; i < onset_times.length - 1; i++) {
      if (onset_times[i] <= time && onset_times[i + 1] >= time) {
        lo = i;
        break;
      }
    }
    const t0 = onset_times[lo];
    const t1 = onset_times[lo + 1] ?? t0;
    const v0 = onset_values[lo] ?? 0;
    const v1 = onset_values[lo + 1] ?? v0;
    if (t1 === t0) return v0;
    const frac = (time - t0) / (t1 - t0);
    return v0 + frac * (v1 - v0);
  }

  return (
    <svg
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      className="w-full"
      aria-label="Beat map"
    >
      <polygon points={fillPoints} fill="#00AAFF" fillOpacity={0.08} />

      <polyline
        points={polylinePoints}
        fill="none"
        stroke="#00AAFF"
        strokeWidth={1.5}
        strokeLinejoin="round"
        strokeLinecap="round"
        opacity={0.8}
      />

      {beat_times.map((bt, i) => {
        const bx = toX(bt);
        const bv = interpolateValue(bt);
        const by = toY(bv);
        const baselineY = HEIGHT - PADDING_TOP;
        return (
          <g key={i}>
            <line
              x1={bx.toFixed(1)}
              y1={by.toFixed(1)}
              x2={bx.toFixed(1)}
              y2={baselineY.toFixed(1)}
              stroke="#00AAFF"
              strokeOpacity={0.2}
              strokeWidth={1}
            />
            <circle
              cx={bx.toFixed(1)}
              cy={by.toFixed(1)}
              r={3}
              fill="#00AAFF"
            />
          </g>
        );
      })}

      <text
        x={WIDTH / 2}
        y={HEIGHT - 2}
        textAnchor="middle"
        fontSize={11}
        fill="#4A5568"
        fontFamily="var(--font-mono)"
      >
        time (s)
      </text>
      <text
        x={0}
        y={PADDING_TOP - 6}
        fontSize={11}
        fill="#4A5568"
        fontFamily="var(--font-mono)"
      >
        onset_strength
      </text>
    </svg>
  );
}
