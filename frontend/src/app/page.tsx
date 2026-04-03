import { HeroVideo } from "@/components/gallery/hero-video";
import { Carousel } from "@/components/gallery/carousel";

/**
 * Gallery landing page — FE-01.
 * Shows hero video with CTA overlay, then carousel of pre-generated examples.
 * Replace EXAMPLES src paths with real pre-generated videos before deployment.
 */

const EXAMPLES = [
  {
    id: "1",
    // Replace with pre-generated videos from backend before deployment
    src: "/examples/tunnel-techno.mp4",
    prompt: "Neon tunnel pulsing to heavy techno beats",
    genre: "Techno",
  },
  {
    id: "2",
    src: "/examples/fractal-ambient.mp4",
    prompt: "Ethereal fractal morphing in soft ambient hues",
    genre: "Ambient",
  },
  {
    id: "3",
    src: "/examples/particles-edm.mp4",
    prompt: "Explosive particle storm synced to EDM drops",
    genre: "EDM",
  },
  {
    id: "4",
    src: "/examples/plasma-jazz.mp4",
    prompt: "Smooth plasma waves flowing with jazz rhythms",
    genre: "Jazz",
  },
  {
    id: "5",
    src: "/examples/tunnel-synthwave.mp4",
    prompt: "Retro synthwave tunnel with neon grids",
    genre: "Synthwave",
  },
  {
    id: "6",
    src: "/examples/fractal-classical.mp4",
    prompt: "Elegant fractal bloom following classical dynamics",
    genre: "Classical",
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
