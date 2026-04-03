"use client";

import { Card, CardHeader, CardContent } from "@/components/ui/card";
import type { BpmVisualization } from "@/lib/types";

interface BpmChartProps {
  visualization: BpmVisualization;
}

export function BpmChart({ visualization }: BpmChartProps) {
  const { onset_times, onset_values, beat_times } = visualization;

  if (!onset_times.length || !onset_values.length) {
    return (
      <Card>
        <CardHeader>
          <p className="text-sm font-semibold text-white/80">BPM Visualization</p>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-white/40">No visualization data available.</p>
        </CardContent>
      </Card>
    );
  }

  const WIDTH = 800;
  const HEIGHT = 200;
  const PADDING_TOP = 20;
  const CHART_HEIGHT = 160;

  const maxTime = Math.max(...onset_times);
  const maxValue = Math.max(...onset_values) || 1;

  // Normalize coordinates
  const toX = (t: number) => (t / maxTime) * WIDTH;
  const toY = (v: number) =>
    HEIGHT - PADDING_TOP - (v / maxValue) * CHART_HEIGHT;

  // Build polyline points string
  const polylinePoints = onset_times
    .map((t, i) => `${toX(t).toFixed(1)},${toY(onset_values[i]).toFixed(1)}`)
    .join(" ");

  // Build filled area polygon (add baseline corners)
  const firstX = toX(onset_times[0]).toFixed(1);
  const lastX = toX(onset_times[onset_times.length - 1]).toFixed(1);
  const baseline = (HEIGHT - PADDING_TOP).toFixed(1);
  const fillPoints = `${firstX},${baseline} ${polylinePoints} ${lastX},${baseline}`;

  // Interpolate onset value at a given time (for beat marker Y position)
  function interpolateValue(time: number): number {
    if (!onset_times.length) return 0;
    // Find surrounding points
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
    <Card>
      <CardHeader>
        <p className="text-sm font-semibold text-white/80">BPM Visualization</p>
      </CardHeader>
      <CardContent>
        <svg
          viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
          className="w-full"
          aria-label="BPM energy timeline"
        >
          {/* Filled area under energy curve */}
          <polygon points={fillPoints} fill="#ec4899" fillOpacity={0.1} />

          {/* Energy timeline polyline */}
          <polyline
            points={polylinePoints}
            fill="none"
            stroke="#ec4899"
            strokeWidth={2}
            strokeLinejoin="round"
            strokeLinecap="round"
          />

          {/* Beat markers */}
          {beat_times.map((bt, i) => {
            const bx = toX(bt);
            const bv = interpolateValue(bt);
            const by = toY(bv);
            const baselineY = HEIGHT - PADDING_TOP;
            return (
              <g key={i}>
                {/* Vertical line from beat to baseline */}
                <line
                  x1={bx.toFixed(1)}
                  y1={by.toFixed(1)}
                  x2={bx.toFixed(1)}
                  y2={baselineY.toFixed(1)}
                  stroke="#f59e0b"
                  strokeOpacity={0.3}
                  strokeWidth={1}
                />
                {/* Beat circle */}
                <circle
                  cx={bx.toFixed(1)}
                  cy={by.toFixed(1)}
                  r={4}
                  fill="#f59e0b"
                />
              </g>
            );
          })}

          {/* Axis labels */}
          <text
            x={WIDTH / 2}
            y={HEIGHT - 2}
            textAnchor="middle"
            fontSize={11}
            fill="rgba(255,255,255,0.4)"
          >
            Time (s)
          </text>
          <text
            x={0}
            y={PADDING_TOP - 6}
            fontSize={11}
            fill="rgba(255,255,255,0.4)"
          >
            Onset Strength
          </text>
        </svg>
      </CardContent>
    </Card>
  );
}
