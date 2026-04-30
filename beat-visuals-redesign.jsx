import { useState, useEffect, useRef } from "react";

// ─── Design Tokens ───────────────────────────────────────────────
const T = {
  bg: "#0A0C10",
  surface: "#12151C",
  elevated: "#1A1E28",
  border: "#252A36",
  borderLight: "#353B4A",
  // Primary: Electric Blue
  primary: "#00AAFF",
  primaryGlow: "rgba(0, 170, 255, 0.15)",
  primaryMuted: "#0088CC",
  primaryBright: "#33BBFF",
  // Secondary: Neon Green (success / energy)
  green: "#00FF88",
  greenGlow: "rgba(0, 255, 136, 0.1)",
  // Tertiary: Violet (creative / AI)
  violet: "#8B5CF6",
  violetGlow: "rgba(139, 92, 246, 0.12)",
  // Accent: Warm Pink (for genre highlights)
  pink: "#FF3399",
  pinkGlow: "rgba(255, 51, 153, 0.1)",
  // Text
  text: "#E2E8F0",
  textMuted: "#8892A4",
  textDim: "#4A5568",
  // Fonts
  mono: "'JetBrains Mono', 'SF Mono', 'Fira Code', monospace",
  sans: "'Space Grotesk', 'Inter', system-ui, sans-serif",
  radius: "3px",
};

// ─── Animated Background Canvas (for Landing page) ───────────────
function AnimatedBackground() {
  const canvasRef = useRef(null);
  const frameRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let animId;

    const resize = () => {
      canvas.width = canvas.offsetWidth * 2;
      canvas.height = canvas.offsetHeight * 2;
      ctx.scale(2, 2);
    };
    resize();

    const draw = () => {
      const w = canvas.offsetWidth;
      const h = canvas.offsetHeight;
      const t = frameRef.current * 0.008;
      frameRef.current++;

      ctx.fillStyle = T.bg;
      ctx.fillRect(0, 0, w, h);

      // Grid lines — cold blue tint
      ctx.strokeStyle = "rgba(0,170,255,0.035)";
      ctx.lineWidth = 0.5;
      const gridSize = 40;
      for (let x = 0; x < w; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
      }
      for (let y = 0; y < h; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }

      // Pulsing circles synced to "beat"
      const bpm = 128;
      const beatPhase = (t * bpm) / 60;
      const pulse = Math.pow(Math.max(0, Math.sin(beatPhase * Math.PI)), 4);

      // Center waveform ring
      const cx = w / 2;
      const cy = h / 2;
      const baseR = 80 + pulse * 30;

      for (let ring = 0; ring < 4; ring++) {
        const r = baseR + ring * 35;
        const alpha = 0.14 - ring * 0.028;
        ctx.beginPath();
        for (let a = 0; a < Math.PI * 2; a += 0.02) {
          const noise =
            Math.sin(a * 8 + t * 2) * 6 * pulse +
            Math.sin(a * 3 - t) * 4;
          const px = cx + Math.cos(a) * (r + noise);
          const py = cy + Math.sin(a) * (r + noise);
          a === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
        }
        ctx.closePath();
        // Alternate between blue and violet rings
        ctx.strokeStyle =
          ring % 2 === 0
            ? `rgba(0, 170, 255, ${alpha})`
            : `rgba(139, 92, 246, ${alpha * 0.7})`;
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }

      // Floating data particles — blue/green/violet
      for (let i = 0; i < 35; i++) {
        const seed = i * 137.508;
        const px =
          (Math.sin(seed + t * 0.3) * 0.5 + 0.5) * w * 0.8 + w * 0.1;
        const py =
          (Math.cos(seed * 0.7 + t * 0.2) * 0.5 + 0.5) * h * 0.8 +
          h * 0.1;
        const size = 1.5 + Math.sin(seed + t) * 0.8;
        const a = 0.15 + pulse * 0.2;
        ctx.fillStyle =
          i % 4 === 0
            ? `rgba(0,170,255,${a})`
            : i % 4 === 1
            ? `rgba(0,255,136,${a * 0.5})`
            : i % 4 === 2
            ? `rgba(139,92,246,${a * 0.6})`
            : `rgba(0,170,255,${a * 0.3})`;
        ctx.beginPath();
        ctx.arc(px, py, size, 0, Math.PI * 2);
        ctx.fill();
      }

      // Scan line effect — blue tinted
      const scanY = (t * 30) % h;
      ctx.fillStyle = "rgba(0,170,255,0.025)";
      ctx.fillRect(0, scanY, w, 2);

      animId = requestAnimationFrame(draw);
    };

    draw();
    window.addEventListener("resize", resize);
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        opacity: 0.7,
      }}
    />
  );
}

// ─── Shared Components ───────────────────────────────────────────

function MonoLabel({ children, color = T.textDim, style = {} }) {
  return (
    <span
      style={{
        fontFamily: T.mono,
        fontSize: "10px",
        letterSpacing: "0.08em",
        textTransform: "uppercase",
        color,
        ...style,
      }}
    >
      {children}
    </span>
  );
}

function Badge({ children, color = T.primary }) {
  return (
    <span
      style={{
        fontFamily: T.mono,
        fontSize: "10px",
        padding: "2px 8px",
        border: `1px solid ${color}40`,
        borderRadius: T.radius,
        color: color,
        background: `${color}10`,
        letterSpacing: "0.05em",
      }}
    >
      {children}
    </span>
  );
}

function Knob({ value = 0.7, label, size = 48, color = T.primary }) {
  const angle = -135 + value * 270;
  const r = size / 2 - 6;
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "6px",
      }}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={T.border}
          strokeWidth="2"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeDasharray={`${value * Math.PI * r * 1.5} ${Math.PI * r * 2}`}
          strokeDashoffset={Math.PI * r * 0.75}
          strokeLinecap="round"
          style={{ filter: `drop-shadow(0 0 4px ${color}60)` }}
        />
        <circle
          cx={size / 2 + Math.cos((angle * Math.PI) / 180) * (r - 2)}
          cy={size / 2 + Math.sin((angle * Math.PI) / 180) * (r - 2)}
          r="3"
          fill={color}
          style={{ filter: `drop-shadow(0 0 3px ${color})` }}
        />
        <text
          x={size / 2}
          y={size / 2 + 1}
          textAnchor="middle"
          dominantBaseline="middle"
          fill={T.text}
          style={{ fontFamily: T.mono, fontSize: "11px" }}
        >
          {Math.round(value * 100)}
        </text>
      </svg>
      <MonoLabel>{label}</MonoLabel>
    </div>
  );
}

function HardwareButton({
  children,
  active,
  onClick,
  variant = "default",
  fullWidth = false,
}) {
  const isPrimary = variant === "primary";
  return (
    <button
      onClick={onClick}
      style={{
        fontFamily: T.mono,
        fontSize: "11px",
        letterSpacing: "0.06em",
        textTransform: "uppercase",
        padding: isPrimary ? "12px 24px" : "8px 16px",
        border: `1px solid ${
          active ? T.primary : isPrimary ? T.primary : T.border
        }`,
        borderRadius: T.radius,
        background: active
          ? T.primaryGlow
          : isPrimary
          ? T.primary
          : "transparent",
        color: active ? T.primary : isPrimary ? "#050810" : T.textMuted,
        cursor: "pointer",
        transition: "all 0.15s ease",
        width: fullWidth ? "100%" : "auto",
        fontWeight: isPrimary ? 700 : 500,
      }}
    >
      {children}
    </button>
  );
}

function ChannelStrip({ label, value, color = T.primary, active = true }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "6px",
        padding: "8px 6px",
        background: active ? `${color}08` : "transparent",
        border: `1px solid ${active ? `${color}30` : T.border}`,
        borderRadius: T.radius,
        minWidth: "54px",
      }}
    >
      <div
        style={{
          width: "4px",
          height: "40px",
          background: T.border,
          borderRadius: "2px",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "absolute",
            bottom: 0,
            width: "100%",
            height: `${value}%`,
            background: color,
            borderRadius: "2px",
            boxShadow: `0 0 6px ${color}60`,
          }}
        />
      </div>
      <MonoLabel color={active ? color : T.textDim}>{label}</MonoLabel>
    </div>
  );
}

// ─── PAGE: Landing ───────────────────────────────────────────────
function LandingPage({ onNavigate }) {
  const [hoveredExample, setHoveredExample] = useState(null);

  const examples = [
    {
      id: 1,
      genre: "TECHNO",
      effect: "TUNNEL",
      bpm: 138,
      color: T.primary,
      prompt: "Neon tunnel pulsing to heavy techno beats",
    },
    {
      id: 2,
      genre: "AMBIENT",
      effect: "FRACTAL",
      bpm: 72,
      color: T.green,
      prompt: "Ethereal fractal morphing in soft ambient hues",
    },
    {
      id: 3,
      genre: "EDM",
      effect: "PARTICLES",
      bpm: 128,
      color: T.violet,
      prompt: "Explosive particle storm synced to EDM drops",
    },
    {
      id: 4,
      genre: "JAZZ",
      effect: "PLASMA",
      bpm: 110,
      color: T.primaryBright,
      prompt: "Smooth plasma waves flowing with jazz rhythms",
    },
    {
      id: 5,
      genre: "SYNTHWAVE",
      effect: "TUNNEL",
      bpm: 118,
      color: T.pink,
      prompt: "Retro synthwave tunnel with neon grids",
    },
  ];

  return (
    <div style={{ position: "relative", minHeight: "100vh" }}>
      {/* ── Hero with animated BG ── */}
      <div
        style={{
          position: "relative",
          height: "70vh",
          overflow: "hidden",
          borderBottom: `1px solid ${T.border}`,
        }}
      >
        <AnimatedBackground />

        {/* Scan lines overlay */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px)",
            pointerEvents: "none",
          }}
        />

        {/* Hero content */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 2,
          }}
        >
          <div
            style={{
              border: `1px solid ${T.border}`,
              borderRadius: T.radius,
              background: "rgba(10,12,16,0.88)",
              backdropFilter: "blur(16px)",
              padding: "32px 48px",
              textAlign: "center",
              maxWidth: "520px",
            }}
          >
            <MonoLabel color={T.primary} style={{ fontSize: "11px" }}>
              sys.beat_visuals v0.1.0
            </MonoLabel>
            <h1
              style={{
                fontFamily: T.sans,
                fontSize: "36px",
                fontWeight: 700,
                color: T.text,
                margin: "12px 0 4px",
                letterSpacing: "-0.02em",
                lineHeight: 1.1,
              }}
            >
              AI-Powered
              <br />
              <span style={{ color: T.primary }}>Beat Visuals</span>
            </h1>
            <p
              style={{
                fontFamily: T.mono,
                fontSize: "12px",
                color: T.textMuted,
                margin: "12px 0 24px",
                lineHeight: 1.6,
              }}
            >
              generate synced video backdrops
              <br />
              for concerts {"&"} parties
            </p>
            <HardwareButton
              variant="primary"
              onClick={() => onNavigate("generate")}
            >
              {"> "}initialize generator
            </HardwareButton>
          </div>
        </div>

        {/* Bottom status bar */}
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            padding: "8px 24px",
            display: "flex",
            justifyContent: "space-between",
            fontFamily: T.mono,
            fontSize: "10px",
            color: T.textDim,
            background: "linear-gradient(transparent, rgba(10,12,16,0.9))",
            zIndex: 2,
          }}
        >
          <span>
            <span style={{ color: T.green }}>●</span> system.online
          </span>
          <span>librosa + rag + llm + opencv</span>
          <span>1080p · 30fps · mp4</span>
        </div>
      </div>

      {/* ── Examples Grid (Ableton session view inspired) ── */}
      <div style={{ padding: "32px 24px" }}>
        <div
          style={{
            display: "flex",
            alignItems: "baseline",
            justifyContent: "space-between",
            marginBottom: "16px",
          }}
        >
          <div style={{ display: "flex", alignItems: "baseline", gap: "12px" }}>
            <MonoLabel color={T.primary}>examples</MonoLabel>
            <MonoLabel>{examples.length} clips loaded</MonoLabel>
          </div>
          <MonoLabel>hover to preview</MonoLabel>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "1px" }}>
          {/* Column headers */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "40px 1fr 90px 70px 60px 48px",
              gap: "1px",
              padding: "6px 0",
              borderBottom: `1px solid ${T.border}`,
            }}
          >
            <MonoLabel style={{ textAlign: "center" }}>#</MonoLabel>
            <MonoLabel>prompt</MonoLabel>
            <MonoLabel>genre</MonoLabel>
            <MonoLabel>effect</MonoLabel>
            <MonoLabel>bpm</MonoLabel>
            <MonoLabel style={{ textAlign: "center" }}>▶</MonoLabel>
          </div>

          {examples.map((ex, i) => (
            <div
              key={ex.id}
              onMouseEnter={() => setHoveredExample(i)}
              onMouseLeave={() => setHoveredExample(null)}
              style={{
                display: "grid",
                gridTemplateColumns: "40px 1fr 90px 70px 60px 48px",
                gap: "1px",
                padding: "10px 0",
                background:
                  hoveredExample === i ? `${ex.color}08` : "transparent",
                borderBottom: `1px solid ${T.border}`,
                cursor: "pointer",
                transition: "background 0.1s",
                alignItems: "center",
              }}
            >
              <span
                style={{
                  fontFamily: T.mono,
                  fontSize: "11px",
                  color: T.textDim,
                  textAlign: "center",
                }}
              >
                {String(i + 1).padStart(2, "0")}
              </span>
              <span
                style={{
                  fontFamily: T.sans,
                  fontSize: "13px",
                  color: hoveredExample === i ? T.text : T.textMuted,
                  transition: "color 0.1s",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {ex.prompt}
              </span>
              <Badge color={ex.color}>{ex.genre}</Badge>
              <span
                style={{
                  fontFamily: T.mono,
                  fontSize: "11px",
                  color: T.textDim,
                }}
              >
                {ex.effect}
              </span>
              <span
                style={{
                  fontFamily: T.mono,
                  fontSize: "12px",
                  color: hoveredExample === i ? ex.color : T.textMuted,
                  transition: "color 0.1s",
                }}
              >
                {ex.bpm}
              </span>
              <div style={{ textAlign: "center" }}>
                <span
                  style={{
                    display: "inline-block",
                    width: "24px",
                    height: "24px",
                    borderRadius: T.radius,
                    border: `1px solid ${
                      hoveredExample === i ? ex.color : T.border
                    }`,
                    color: hoveredExample === i ? ex.color : T.textDim,
                    fontSize: "10px",
                    lineHeight: "22px",
                    textAlign: "center",
                    transition: "all 0.1s",
                    background:
                      hoveredExample === i ? `${ex.color}15` : "transparent",
                  }}
                >
                  ▶
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── PAGE: Generate ──────────────────────────────────────────────
function GeneratePage({ onNavigate }) {
  const [prompt, setPrompt] = useState("");
  const [selectedGenreA, setSelectedGenreA] = useState("Techno");
  const [selectedGenreB, setSelectedGenreB] = useState("Ambient");
  const [blend, setBlend] = useState(70);
  const [bpm, setBpm] = useState(128);

  const genres = [
    "Techno",
    "Ambient",
    "EDM",
    "Jazz",
    "Synthwave",
    "Classical",
    "DnB",
    "House",
    "Lo-fi",
    "Metal",
  ];

  return (
    <div style={{ padding: "24px", maxWidth: "960px", margin: "0 auto" }}>
      {/* Page header */}
      <div style={{ marginBottom: "24px" }}>
        <MonoLabel color={T.primary}>module::generate</MonoLabel>
        <h1
          style={{
            fontFamily: T.sans,
            fontSize: "24px",
            fontWeight: 700,
            color: T.text,
            marginTop: "4px",
          }}
        >
          Create Backdrop
        </h1>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 280px",
          gap: "24px",
        }}
      >
        {/* ── Left: Controls ── */}
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {/* Prompt input — terminal style */}
          <div
            style={{
              border: `1px solid ${T.border}`,
              borderRadius: T.radius,
              background: T.surface,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                padding: "8px 12px",
                borderBottom: `1px solid ${T.border}`,
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <MonoLabel color={T.primary}>visual_prompt</MonoLabel>
              <MonoLabel>{prompt.length}/500</MonoLabel>
            </div>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="> describe your visual style..."
              style={{
                width: "100%",
                minHeight: "100px",
                padding: "12px",
                background: "transparent",
                border: "none",
                color: T.text,
                fontFamily: T.mono,
                fontSize: "13px",
                lineHeight: 1.6,
                resize: "vertical",
                outline: "none",
              }}
            />
          </div>

          {/* Genre Blend — Ableton channel mixer style */}
          <div
            style={{
              border: `1px solid ${T.border}`,
              borderRadius: T.radius,
              background: T.surface,
              padding: "16px",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: "12px",
              }}
            >
              <MonoLabel color={T.primary}>style_blend</MonoLabel>
              <MonoLabel>
                {selectedGenreA} × {selectedGenreB}
              </MonoLabel>
            </div>

            {/* Genre A selector */}
            <MonoLabel style={{ marginBottom: "6px", display: "block" }}>
              channel_a
            </MonoLabel>
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "4px",
                marginBottom: "16px",
              }}
            >
              {genres.map((g) => (
                <HardwareButton
                  key={`a-${g}`}
                  active={selectedGenreA === g}
                  onClick={() => setSelectedGenreA(g)}
                >
                  {g}
                </HardwareButton>
              ))}
            </div>

            {/* Blend slider */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                margin: "8px 0",
              }}
            >
              <MonoLabel color={T.primary}>{100 - blend}%</MonoLabel>
              <div
                style={{
                  flex: 1,
                  height: "6px",
                  background: T.elevated,
                  borderRadius: "3px",
                  position: "relative",
                  cursor: "pointer",
                }}
                onClick={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect();
                  const pct = Math.round(
                    ((e.clientX - rect.left) / rect.width) * 100
                  );
                  setBlend(Math.max(0, Math.min(100, pct)));
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    left: 0,
                    top: 0,
                    height: "100%",
                    width: `${blend}%`,
                    background: `linear-gradient(90deg, ${T.primary}, ${T.violet})`,
                    borderRadius: "3px",
                    boxShadow: `0 0 8px ${T.primaryGlow}`,
                  }}
                />
                <div
                  style={{
                    position: "absolute",
                    top: "-5px",
                    left: `${blend}%`,
                    transform: "translateX(-50%)",
                    width: "16px",
                    height: "16px",
                    background: T.bg,
                    border: `2px solid ${T.primary}`,
                    borderRadius: "2px",
                  }}
                />
              </div>
              <MonoLabel color={T.violet}>{blend}%</MonoLabel>
            </div>

            {/* Genre B selector */}
            <MonoLabel style={{ marginBottom: "6px", display: "block" }}>
              channel_b
            </MonoLabel>
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "4px",
              }}
            >
              {genres.map((g) => (
                <HardwareButton
                  key={`b-${g}`}
                  active={selectedGenreB === g}
                  onClick={() => setSelectedGenreB(g)}
                >
                  {g}
                </HardwareButton>
              ))}
            </div>
          </div>

          {/* BPM + Audio — hardware panel */}
          <div
            style={{
              border: `1px solid ${T.border}`,
              borderRadius: T.radius,
              background: T.surface,
              padding: "16px",
            }}
          >
            <MonoLabel color={T.primary}>tempo_config</MonoLabel>

            <div
              style={{
                display: "flex",
                alignItems: "flex-end",
                gap: "24px",
                marginTop: "12px",
              }}
            >
              {/* BPM display — big number like TE */}
              <div>
                <div
                  style={{
                    fontFamily: T.mono,
                    fontSize: "48px",
                    fontWeight: 700,
                    color: T.primary,
                    lineHeight: 1,
                    letterSpacing: "-0.03em",
                    textShadow: `0 0 20px ${T.primaryGlow}`,
                  }}
                >
                  {bpm}
                </div>
                <MonoLabel>bpm</MonoLabel>
              </div>

              {/* Quick buttons */}
              <div
                style={{
                  display: "flex",
                  gap: "4px",
                  paddingBottom: "4px",
                }}
              >
                {[64, 90, 110, 128, 140, 174].map((b) => (
                  <HardwareButton
                    key={b}
                    active={bpm === b}
                    onClick={() => setBpm(b)}
                  >
                    {b}
                  </HardwareButton>
                ))}
              </div>

              {/* Knobs */}
              <div
                style={{ display: "flex", gap: "12px", marginLeft: "auto" }}
              >
                <Knob value={0.65} label="intensity" size={48} />
                <Knob
                  value={0.4}
                  label="complexity"
                  size={48}
                  color={T.violet}
                />
              </div>
            </div>

            {/* Audio upload zone */}
            <div
              style={{
                marginTop: "16px",
                padding: "16px",
                border: `1px dashed ${T.border}`,
                borderRadius: T.radius,
                textAlign: "center",
                cursor: "pointer",
              }}
            >
              <MonoLabel>drop audio file or click to upload</MonoLabel>
              <div
                style={{
                  fontFamily: T.mono,
                  fontSize: "10px",
                  color: T.textDim,
                  marginTop: "4px",
                }}
              >
                .mp3 .wav .ogg · max 10mb · auto-detects bpm
              </div>
            </div>
          </div>

          {/* Submit */}
          <HardwareButton
            variant="primary"
            fullWidth
            onClick={() => onNavigate("results")}
          >
            {"> "}execute render pipeline
          </HardwareButton>
        </div>

        {/* ── Right: Live Preview Panel ── */}
        <div
          style={{
            border: `1px solid ${T.border}`,
            borderRadius: T.radius,
            background: T.surface,
            padding: "12px",
            position: "sticky",
            top: "72px",
            height: "fit-content",
          }}
        >
          <MonoLabel color={T.primary}>preview</MonoLabel>

          {/* Mini preview area */}
          <div
            style={{
              marginTop: "8px",
              aspectRatio: "16/9",
              background: T.bg,
              borderRadius: T.radius,
              border: `1px solid ${T.border}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              overflow: "hidden",
              position: "relative",
            }}
          >
            <div
              style={{
                position: "absolute",
                inset: 0,
                background: `radial-gradient(circle at 50% 50%, ${T.primaryGlow}, transparent 70%)`,
              }}
            />
            <MonoLabel color={T.textDim}>live_preview</MonoLabel>
          </div>

          {/* Parameter readout */}
          <div style={{ marginTop: "12px" }}>
            <MonoLabel color={T.textDim}>parameters</MonoLabel>
            <div
              style={{
                marginTop: "8px",
                fontFamily: T.mono,
                fontSize: "11px",
                lineHeight: 2,
                color: T.textMuted,
              }}
            >
              <div>
                <span style={{ color: T.textDim }}>genre_a:</span>{" "}
                <span style={{ color: T.primary }}>
                  {selectedGenreA.toLowerCase()}
                </span>
              </div>
              <div>
                <span style={{ color: T.textDim }}>genre_b:</span>{" "}
                <span style={{ color: T.violet }}>
                  {selectedGenreB.toLowerCase()}
                </span>
              </div>
              <div>
                <span style={{ color: T.textDim }}>blend:</span> {blend}%
              </div>
              <div>
                <span style={{ color: T.textDim }}>tempo:</span> {bpm} bpm
              </div>
              <div>
                <span style={{ color: T.textDim }}>resolution:</span> 1080p
              </div>
              <div>
                <span style={{ color: T.textDim }}>fps:</span> 30
              </div>
            </div>
          </div>

          {/* Channel strip meters */}
          <div style={{ marginTop: "16px" }}>
            <MonoLabel color={T.textDim}>levels</MonoLabel>
            <div
              style={{
                display: "flex",
                gap: "4px",
                marginTop: "8px",
                justifyContent: "center",
              }}
            >
              <ChannelStrip label="bass" value={75} color={T.primary} />
              <ChannelStrip label="mid" value={55} color={T.primary} />
              <ChannelStrip label="high" value={40} color={T.violet} />
              <ChannelStrip label="fx" value={60} color={T.green} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── PAGE: Results ───────────────────────────────────────────────
function ResultsPage({ onNavigate }) {
  const [progress, setProgress] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) {
          setDone(true);
          clearInterval(interval);
          return 100;
        }
        return p + 2;
      });
    }, 80);
    return () => clearInterval(interval);
  }, []);

  const steps = [
    { label: "audio_analysis", threshold: 15 },
    { label: "rag_retrieval", threshold: 30 },
    { label: "llm_blending", threshold: 50 },
    { label: "frame_render", threshold: 85 },
    { label: "encode_mp4", threshold: 95 },
  ];

  const currentStep =
    steps.findIndex((s) => progress < s.threshold) === -1
      ? steps.length - 1
      : Math.max(0, steps.findIndex((s) => progress < s.threshold));

  return (
    <div style={{ padding: "24px", maxWidth: "960px", margin: "0 auto" }}>
      <div style={{ marginBottom: "24px" }}>
        <MonoLabel color={T.primary}>module::render</MonoLabel>
        <h1
          style={{
            fontFamily: T.sans,
            fontSize: "24px",
            fontWeight: 700,
            color: T.text,
            marginTop: "4px",
          }}
        >
          {done ? "Render Complete" : "Rendering..."}
        </h1>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 280px",
          gap: "24px",
        }}
      >
        {/* Left: Video + Progress */}
        <div>
          {/* Video area */}
          <div
            style={{
              aspectRatio: "16/9",
              background: T.surface,
              border: `1px solid ${T.border}`,
              borderRadius: T.radius,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              position: "relative",
              overflow: "hidden",
            }}
          >
            {done ? (
              <>
                <div
                  style={{
                    position: "absolute",
                    inset: 0,
                    background: `radial-gradient(circle at 50% 50%, ${T.primaryGlow}, transparent 60%), radial-gradient(circle at 30% 70%, ${T.violetGlow}, transparent 50%), ${T.bg}`,
                  }}
                />
                <div
                  style={{
                    position: "relative",
                    zIndex: 1,
                    textAlign: "center",
                  }}
                >
                  <div
                    style={{
                      width: "56px",
                      height: "56px",
                      border: `2px solid ${T.primary}`,
                      borderRadius: "50%",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      margin: "0 auto 8px",
                      cursor: "pointer",
                      background: T.primaryGlow,
                    }}
                  >
                    <span
                      style={{
                        color: T.primary,
                        fontSize: "20px",
                        marginLeft: "3px",
                      }}
                    >
                      ▶
                    </span>
                  </div>
                  <MonoLabel color={T.textMuted}>click to play</MonoLabel>
                </div>
              </>
            ) : (
              <div style={{ textAlign: "center" }}>
                <div
                  style={{
                    fontFamily: T.mono,
                    fontSize: "36px",
                    fontWeight: 700,
                    color: T.primary,
                    textShadow: `0 0 30px ${T.primaryGlow}`,
                  }}
                >
                  {progress}%
                </div>
                <MonoLabel color={T.textMuted}>
                  {steps[currentStep]?.label}
                </MonoLabel>
              </div>
            )}
          </div>

          {/* Progress bar — detailed pipeline view */}
          <div
            style={{
              marginTop: "12px",
              border: `1px solid ${T.border}`,
              borderRadius: T.radius,
              background: T.surface,
              padding: "12px",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: "8px",
              }}
            >
              <MonoLabel color={T.primary}>pipeline</MonoLabel>
              <MonoLabel>{done ? "complete" : `${progress}%`}</MonoLabel>
            </div>

            <div
              style={{
                height: "4px",
                background: T.elevated,
                borderRadius: "2px",
                overflow: "hidden",
                marginBottom: "12px",
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${progress}%`,
                  background: done
                    ? T.green
                    : `linear-gradient(90deg, ${T.primary}, ${T.violet})`,
                  transition: "width 0.1s",
                  boxShadow: done
                    ? `0 0 10px ${T.greenGlow}`
                    : `0 0 10px ${T.primaryGlow}`,
                }}
              />
            </div>

            {/* Step indicators */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
              }}
            >
              {steps.map((step, i) => {
                const stepDone = progress >= step.threshold;
                const isCurrent =
                  !stepDone &&
                  (i === 0 || progress >= steps[i - 1].threshold);
                return (
                  <div
                    key={step.label}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "4px",
                    }}
                  >
                    <span
                      style={{
                        width: "6px",
                        height: "6px",
                        borderRadius: "1px",
                        background: stepDone
                          ? T.green
                          : isCurrent
                          ? T.primary
                          : T.border,
                        boxShadow: isCurrent
                          ? `0 0 6px ${T.primary}`
                          : "none",
                      }}
                    />
                    <MonoLabel
                      color={
                        stepDone
                          ? T.green
                          : isCurrent
                          ? T.primary
                          : T.textDim
                      }
                    >
                      {step.label}
                    </MonoLabel>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Action buttons */}
          {done && (
            <div
              style={{
                display: "flex",
                gap: "8px",
                marginTop: "12px",
              }}
            >
              <HardwareButton variant="primary">
                {"> "}download .mp4
              </HardwareButton>
              <HardwareButton onClick={() => onNavigate("generate")}>
                new render
              </HardwareButton>
            </div>
          )}
        </div>

        {/* Right: Metadata panel */}
        <div
          style={{
            border: `1px solid ${T.border}`,
            borderRadius: T.radius,
            background: T.surface,
            padding: "12px",
            height: "fit-content",
          }}
        >
          {/* AI Vision */}
          <MonoLabel color={T.violet}>ai_vision</MonoLabel>
          <p
            style={{
              fontFamily: T.sans,
              fontSize: "13px",
              color: T.textMuted,
              marginTop: "8px",
              lineHeight: 1.6,
            }}
          >
            Deep neon tunnel geometry pulsing in sync with 128bpm techno
            rhythms. Concentric hexagonal rings contract on each beat while
            particle trails trace the frequency spectrum.
          </p>

          {/* Matched styles */}
          <div style={{ marginTop: "16px" }}>
            <MonoLabel color={T.primary}>matched_styles</MonoLabel>
            <div
              style={{
                display: "flex",
                gap: "4px",
                flexWrap: "wrap",
                marginTop: "8px",
              }}
            >
              <Badge color={T.primary}>TECHNO</Badge>
              <Badge color={T.violet}>AMBIENT</Badge>
              <Badge color={T.green}>TUNNEL</Badge>
            </div>
          </div>

          {/* BPM visualization */}
          <div style={{ marginTop: "16px" }}>
            <MonoLabel color={T.primary}>beat_map</MonoLabel>
            <svg
              width="100%"
              height="60"
              viewBox="0 0 256 60"
              style={{ marginTop: "8px" }}
            >
              {/* Energy line */}
              <polyline
                points={Array.from({ length: 64 }, (_, i) => {
                  const x = (i / 63) * 256;
                  const y =
                    30 +
                    Math.sin(i * 0.4) * 12 +
                    Math.sin(i * 0.15) * 8;
                  return `${x},${y}`;
                }).join(" ")}
                fill="none"
                stroke={T.primary}
                strokeWidth="1.5"
                opacity="0.6"
              />
              {/* Beat markers */}
              {[32, 64, 96, 128, 160, 192, 224].map((x) => (
                <line
                  key={x}
                  x1={x}
                  y1="0"
                  x2={x}
                  y2="60"
                  stroke={T.primary}
                  strokeWidth="0.5"
                  opacity="0.2"
                />
              ))}
            </svg>
          </div>

          {/* Render info */}
          <div style={{ marginTop: "16px" }}>
            <MonoLabel color={T.primary}>render_info</MonoLabel>
            <div
              style={{
                fontFamily: T.mono,
                fontSize: "11px",
                lineHeight: 2,
                color: T.textMuted,
                marginTop: "8px",
              }}
            >
              <div>
                <span style={{ color: T.textDim }}>resolution:</span>{" "}
                1920×1080
              </div>
              <div>
                <span style={{ color: T.textDim }}>fps:</span> 30
              </div>
              <div>
                <span style={{ color: T.textDim }}>duration:</span> 30s loop
              </div>
              <div>
                <span style={{ color: T.textDim }}>codec:</span> h264
              </div>
              <div>
                <span style={{ color: T.textDim }}>size:</span> ~12mb
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── App Shell ───────────────────────────────────────────────────
export default function App() {
  const [page, setPage] = useState("landing");

  return (
    <div
      style={{
        background: T.bg,
        color: T.text,
        minHeight: "100vh",
        fontFamily: T.sans,
      }}
    >
      {/* ── Top Bar (hardware device style) ── */}
      <header
        style={{
          position: "sticky",
          top: 0,
          zIndex: 50,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 24px",
          height: "48px",
          borderBottom: `1px solid ${T.border}`,
          background: "rgba(10,12,16,0.92)",
          backdropFilter: "blur(12px)",
        }}
      >
        {/* Logo */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            cursor: "pointer",
          }}
          onClick={() => setPage("landing")}
        >
          <div
            style={{
              width: "20px",
              height: "20px",
              border: `2px solid ${T.primary}`,
              borderRadius: "2px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <span
              style={{
                fontFamily: T.mono,
                fontSize: "10px",
                fontWeight: 700,
                color: T.primary,
              }}
            >
              BV
            </span>
          </div>
          <span
            style={{
              fontFamily: T.mono,
              fontSize: "12px",
              fontWeight: 600,
              color: T.text,
              letterSpacing: "0.04em",
            }}
          >
            beat_visuals
          </span>
        </div>

        {/* Nav */}
        <nav style={{ display: "flex", gap: "2px" }}>
          {[
            { id: "landing", label: "gallery" },
            { id: "generate", label: "generate" },
            { id: "results", label: "output" },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setPage(item.id)}
              style={{
                fontFamily: T.mono,
                fontSize: "11px",
                letterSpacing: "0.04em",
                padding: "6px 14px",
                border: `1px solid ${
                  page === item.id ? T.primary : T.border
                }`,
                borderRadius: T.radius,
                background:
                  page === item.id ? T.primaryGlow : "transparent",
                color: page === item.id ? T.primary : T.textMuted,
                cursor: "pointer",
                transition: "all 0.12s ease",
                textTransform: "uppercase",
              }}
            >
              {item.label}
            </button>
          ))}
        </nav>

        {/* Status indicators */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <span
              style={{
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                background: T.green,
                boxShadow: `0 0 6px ${T.green}60`,
              }}
            />
            <MonoLabel color={T.textMuted}>api</MonoLabel>
          </div>
          <MonoLabel color={T.textDim}>v0.1.0</MonoLabel>
        </div>
      </header>

      {/* ── Page Content ── */}
      {page === "landing" && <LandingPage onNavigate={setPage} />}
      {page === "generate" && <GeneratePage onNavigate={setPage} />}
      {page === "results" && <ResultsPage onNavigate={setPage} />}
    </div>
  );
}
