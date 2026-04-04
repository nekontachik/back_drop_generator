import { HeroVideo } from "@/components/gallery/hero-video";
import { Carousel } from "@/components/gallery/carousel";

/**
 * Gallery landing page — FE-01.
 * Shows hero video with CTA overlay, then carousel of pre-generated examples.
 * Run backend/scripts/generate_gallery.py to produce the videos in frontend/public/examples/.
 */

const EXAMPLES = [
  {
    id: "1",
    src: "/examples/tunnel-techno.mp4",
    prompt: "Neon tunnel pulsing to heavy techno beats",
    genre: "Techno",
    effect: "tunnel",
    bpm: 138,
  },
  {
    id: "2",
    src: "/examples/fractal-ambient.mp4",
    prompt: "Ethereal fractal morphing in soft ambient hues",
    genre: "Ambient",
    effect: "fractal",
    bpm: 72,
  },
  {
    id: "3",
    src: "/examples/particles-edm.mp4",
    prompt: "Explosive particle storm synced to EDM drops",
    genre: "EDM",
    effect: "particles",
    bpm: 128,
  },
  {
    id: "4",
    src: "/examples/plasma-jazz.mp4",
    prompt: "Smooth plasma waves flowing with jazz rhythms",
    genre: "Jazz",
    effect: "plasma",
    bpm: 110,
  },
  {
    id: "5",
    src: "/examples/tunnel-synthwave.mp4",
    prompt: "Retro synthwave tunnel with neon grids",
    genre: "Synthwave",
    effect: "tunnel",
    bpm: 118,
  },
  {
    id: "6",
    src: "/examples/fractal-classical.mp4",
    prompt: "Elegant fractal bloom following classical dynamics",
    genre: "Classical",
    effect: "fractal",
    bpm: 90,
  },
];

export default function GalleryPage() {
  return (
    <main className="min-h-screen">
      {/* Hero video section with CTA overlay */}
      <HeroVideo
        // Hero video will show gradient fallback until pre-generated examples are added
        src={undefined}
        posterSrc={undefined}
      />

      {/* Example carousel */}
      <Carousel items={EXAMPLES} />
    </main>
  );
}
