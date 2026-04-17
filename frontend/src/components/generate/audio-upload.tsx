"use client";

import { useDropzone } from "react-dropzone";
import { X } from "lucide-react";
import { useCallback } from "react";
import { MonoLabel } from "@/components/ui/mono-label";

interface AudioUploadProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function AudioUpload({ file, onFileChange }: AudioUploadProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileChange(acceptedFiles[0]);
      }
    },
    [onFileChange]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "audio/*": [".mp3", ".wav", ".m4a", ".ogg", ".flac"] },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
  });

  if (file) {
    return (
      <div className="border border-dashed border-primary/40 rounded-sm p-3 flex items-center gap-3 bg-primary/[0.04]">
        <div className="flex-1 min-w-0">
          <p className="font-mono text-[12px] text-text truncate">
            {file.name}
          </p>
          <p className="font-mono text-[10px] text-text-dim mt-0.5">
            {formatBytes(file.size)} · loaded
          </p>
        </div>
        <button
          type="button"
          onClick={() => onFileChange(null)}
          className="flex-shrink-0 w-7 h-7 rounded-sm flex items-center justify-center text-text-dim hover:text-text hover:bg-border transition-colors"
          aria-label="Remove file"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={`border border-dashed rounded-sm p-4 text-center cursor-pointer transition-colors ${
        isDragActive
          ? "border-primary bg-primary/[0.06]"
          : "border-border hover:border-border-light"
      }`}
    >
      <input {...getInputProps()} />
      <MonoLabel color="var(--color-text-muted)">
        drop audio file or click to upload
      </MonoLabel>
      <div className="font-mono text-[10px] text-text-dim mt-1">
        .mp3 .wav .ogg · max 10mb · auto-detects bpm
      </div>
    </div>
  );
}
