/**
 * TypeScript types mirroring backend Pydantic models.
 * Keep in sync with backend/app/models/audio.py and backend/app/models/api.py
 */

export interface BpmResult {
  detected: number;
  half: number;
  double: number;
}

export interface MoodVector {
  spectral_centroid: number;
  chroma: number[]; // 12 pitch classes
  rms: number;
  onset_strength: number;
  labels: string[]; // ["bright"/"dark", "energetic"/"mellow", "dense"/"sparse"]
}

export interface BpmVisualization {
  onset_times: number[];
  onset_values: number[];
  beat_times: number[];
}

export interface AudioAnalysis {
  bpm: BpmResult;
  beat_times: number[];
  mood: MoodVector;
  visualization: BpmVisualization;
}

export interface StyleMatch {
  id: string;
  genre: string;
  description: string;
  colors: string[];
  shapes: string[];
  movement: string;
  intensity: number;
  speed: number;
  distance: number;
}

export interface GenerateResponse {
  job_id: string;
  audio_analysis: AudioAnalysis | null;
  matched_styles: StyleMatch[] | null;
}

export interface JobStatusResponse {
  job_id: string;
  status: string;
  progress: number;
  error: string | null;
}

export type JobStatus = "pending" | "rendering" | "complete" | "failed";
