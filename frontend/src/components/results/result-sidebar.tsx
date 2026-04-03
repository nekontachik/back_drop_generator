"use client";

import Link from "next/link";
import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { BpmChart } from "./bpm-chart";
import { getDownloadUrl } from "@/lib/api";
import type { AudioAnalysis, StyleMatch } from "@/lib/types";

interface ResultSidebarProps {
  jobId: string;
  audioAnalysis: AudioAnalysis | null;
  matchedStyles: StyleMatch[] | null;
}

export function ResultSidebar({ jobId, audioAnalysis, matchedStyles }: ResultSidebarProps) {
  return (
    <div className="flex flex-col gap-4">
      {/* BPM Chart */}
      {audioAnalysis && (
        <BpmChart visualization={audioAnalysis.visualization} />
      )}

      {/* Genre Matches */}
      {matchedStyles && matchedStyles.length > 0 && (
        <Card>
          <CardHeader>
            <p className="text-sm font-semibold text-white/80">Matched Styles</p>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-4">
              {matchedStyles.map((style) => (
                <div key={style.id} className="flex flex-col gap-1">
                  <p className="font-semibold text-white capitalize">{style.genre}</p>
                  <p className="text-sm text-white/60">{style.description}</p>
                  {style.colors.length > 0 && (
                    <div className="flex items-center gap-1 mt-1 flex-wrap">
                      {style.colors.map((color, idx) => (
                        <div
                          key={idx}
                          className="w-4 h-4 rounded-full border border-white/10"
                          style={{ backgroundColor: color }}
                          title={color}
                        />
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Download */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-col gap-3">
            <a href={getDownloadUrl(jobId)} download className="w-full">
              <Button className="w-full" size="lg">
                <Download className="mr-2 h-4 w-4" />
                Download MP4
              </Button>
            </a>
            <Link href="/generate" className="w-full">
              <Button variant="outline" className="w-full" size="lg">
                Generate Another
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
