"use client";

import { useDropzone } from "react-dropzone";
import { Upload, X, FileAudio } from "lucide-react";
import { useCallback } from "react";

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
      <div className="border-2 border-dashed border-white/20 rounded-xl p-6 flex items-center gap-4">
        <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-accent-amber/10 flex items-center justify-center">
          <FileAudio className="w-5 h-5 text-accent-amber" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-white truncate">{file.name}</p>
          <p className="text-xs text-white/40">{formatBytes(file.size)}</p>
        </div>
        <button
          type="button"
          onClick={() => onFileChange(null)}
          className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 transition-colors"
          aria-label="Remove file"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
        isDragActive
          ? "border-accent-amber bg-accent-amber/5"
          : "border-white/20 hover:border-accent-amber/50"
      }`}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-3">
        <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center">
          <Upload className="w-6 h-6 text-white/40" />
        </div>
        <div>
          <p className="text-sm font-medium text-white">Drop audio file here</p>
          <p className="text-xs text-white/40 mt-1">or click to browse</p>
        </div>
        <p className="text-xs text-white/30">MP3, WAV, M4A, OGG, FLAC up to 10MB</p>
      </div>
    </div>
  );
}
