/**
 * API client functions for all backend endpoints.
 * Base URL is configured via NEXT_PUBLIC_API_URL environment variable.
 */
import type { GenerateResponse, JobStatusResponse, StyleMatch } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Submit a generation request (multipart form-data).
 * FormData should include: prompt, bpm, bpm_override, width, height, seed, audio (optional)
 */
export async function submitGenerate(formData: FormData): Promise<GenerateResponse> {
  const res = await fetch(`${API_URL}/generate`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

/**
 * Get the current status of a render job.
 */
export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const res = await fetch(`${API_URL}/jobs/${jobId}`);
  if (!res.ok) throw new Error("Job not found");
  return res.json();
}

/**
 * Open an SSE stream for real-time render progress updates.
 * Event: "progress", data: { job_id, status, progress, error }
 */
export function getJobStream(jobId: string): EventSource {
  return new EventSource(`${API_URL}/jobs/${jobId}/stream`);
}

/**
 * Retrieve style documents matching the given prompt via RAG.
 */
export async function getStyles(prompt: string, nResults = 3): Promise<StyleMatch[]> {
  const res = await fetch(
    `${API_URL}/styles?prompt=${encodeURIComponent(prompt)}&n_results=${nResults}`
  );
  if (!res.ok) return [];
  return res.json();
}

/**
 * Get the download URL for a completed render job's MP4 file.
 */
export function getDownloadUrl(jobId: string): string {
  return `${API_URL}/jobs/${jobId}/download`;
}
