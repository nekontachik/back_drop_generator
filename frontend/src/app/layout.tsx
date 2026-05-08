import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Space_Grotesk } from "next/font/google";
import { Header } from "@/components/layout/header";
import { PageTransition } from "@/components/layout/page-transition";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Beat Visuals — AI Music-Synced Video Generator",
  description:
    "AI backdrop generator that turns music into synced animated video. Audio analysis with librosa, RAG over ChromaDB, Claude API for creative blending, custom render engine producing 1080p mp4 loops.",
  metadataBase: new URL("https://backdropgenerator.vercel.app"),
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
  openGraph: {
    title: "Beat Visuals — AI Music-Synced Video Generator",
    description:
      "AI backdrop generator that turns music into synced animated video. Audio analysis with librosa, RAG over ChromaDB, Claude API for creative blending, custom render engine producing 1080p mp4 loops.",
    url: "https://backdropgenerator.vercel.app",
    siteName: "Beat Visuals",
    type: "website",
    locale: "en_US",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Beat Visuals — AI-powered music-synced video backdrop generator",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Beat Visuals — AI Music-Synced Video Generator",
    description:
      "AI backdrop generator that turns music into synced animated video loops for concerts and parties.",
    images: ["/og-image.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${spaceGrotesk.variable} ${jetbrainsMono.variable} dark`}
    >
      <body className="bg-surface text-white min-h-screen antialiased">
        <Header />
        <PageTransition>{children}</PageTransition>
      </body>
    </html>
  );
}
