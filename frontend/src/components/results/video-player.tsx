"use client";

interface VideoPlayerProps {
  src: string;
  poster?: string;
}

export function VideoPlayer({ src, poster }: VideoPlayerProps) {
  return (
    <div className="w-full rounded-xl overflow-hidden bg-black aspect-video">
      <video
        className="w-full h-full"
        controls
        loop
        poster={poster}
      >
        <source src={src} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
    </div>
  );
}
