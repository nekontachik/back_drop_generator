import type { Metadata } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import { Header } from "@/components/layout/header";
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

export const metadata: Metadata = {
  title: "Beat Visuals",
  description: "AI-powered backdrop generator for concerts and parties",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${spaceGrotesk.variable} dark`}
    >
      <body className="bg-surface text-white min-h-screen antialiased">
        <Header />
        {children}
      </body>
    </html>
  );
}
