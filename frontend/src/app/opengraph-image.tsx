import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt =
  "Beat Visuals — AI Music-Synced Video Generator for concerts and parties";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          background: "linear-gradient(145deg, #0A0C10 0%, #12151C 50%, #0A0C10 100%)",
          fontFamily: "system-ui, sans-serif",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Grid pattern overlay */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            backgroundImage:
              "linear-gradient(rgba(0,170,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0,170,255,0.05) 1px, transparent 1px)",
            backgroundSize: "40px 40px",
          }}
        />

        {/* Glow accent top-left */}
        <div
          style={{
            position: "absolute",
            top: -120,
            left: -120,
            width: 400,
            height: 400,
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(0,170,255,0.15) 0%, transparent 70%)",
            display: "flex",
          }}
        />

        {/* Glow accent bottom-right */}
        <div
          style={{
            position: "absolute",
            bottom: -100,
            right: -100,
            width: 350,
            height: 350,
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%)",
            display: "flex",
          }}
        />

        {/* Waveform bars */}
        <div
          style={{
            display: "flex",
            gap: 12,
            alignItems: "center",
            marginBottom: 40,
          }}
        >
          {[0.3, 0.55, 0.75, 1, 0.85, 0.6, 0.9, 1, 0.7, 0.45, 0.8, 0.95, 0.65, 0.4, 0.25].map(
            (h, i) => (
              <div
                key={i}
                style={{
                  width: 8,
                  height: Math.round(h * 100),
                  borderRadius: 4,
                  background:
                    i < 5
                      ? `rgba(0,170,255,${0.4 + h * 0.6})`
                      : i < 10
                        ? `rgba(139,92,246,${0.4 + h * 0.6})`
                        : `rgba(0,255,136,${0.4 + h * 0.6})`,
                  display: "flex",
                }}
              />
            )
          )}
        </div>

        {/* Logo mark + title */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            marginBottom: 16,
          }}
        >
          {/* BV logo mark */}
          <div
            style={{
              width: 52,
              height: 52,
              borderRadius: 3,
              border: "2px solid #00AAFF",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 22,
              fontWeight: 700,
              color: "#00AAFF",
              letterSpacing: "-0.02em",
            }}
          >
            BV
          </div>
          <div
            style={{
              fontSize: 56,
              fontWeight: 700,
              color: "#E2E8F0",
              letterSpacing: "-0.02em",
              display: "flex",
            }}
          >
            Beat Visuals
          </div>
        </div>

        {/* Subtitle */}
        <div
          style={{
            fontSize: 24,
            color: "#8892A4",
            letterSpacing: "0.05em",
            textTransform: "uppercase" as const,
            display: "flex",
            marginBottom: 48,
          }}
        >
          AI Music-Synced Video Generator
        </div>

        {/* Tech badges */}
        <div style={{ display: "flex", gap: 12 }}>
          {["librosa", "RAG + ChromaDB", "Claude API", "OpenCV"].map((label) => (
            <div
              key={label}
              style={{
                padding: "8px 18px",
                borderRadius: 3,
                border: "1px solid #252A36",
                background: "rgba(18,21,28,0.8)",
                color: "#8892A4",
                fontSize: 14,
                letterSpacing: "0.04em",
                display: "flex",
              }}
            >
              {label}
            </div>
          ))}
        </div>

        {/* Bottom domain */}
        <div
          style={{
            position: "absolute",
            bottom: 32,
            right: 40,
            fontSize: 16,
            color: "#4A5568",
            display: "flex",
          }}
        >
          backdropgenerator.vercel.app
        </div>
      </div>
    ),
    { ...size }
  );
}
