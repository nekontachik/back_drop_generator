export const GENRE_COLORS: Record<string, string> = {
  Techno: "#00AAFF",
  Ambient: "#00FF88",
  EDM: "#8B5CF6",
  Jazz: "#33BBFF",
  Synthwave: "#FF3399",
  Classical: "#8B5CF6",
};

const DEFAULT_GENRE_COLOR = "#00AAFF";

export function genreColor(genre: string): string {
  return GENRE_COLORS[genre] ?? DEFAULT_GENRE_COLOR;
}
