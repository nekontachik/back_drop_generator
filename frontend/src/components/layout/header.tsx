"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { MonoLabel } from "@/components/ui/mono-label";

const navLinks = [
  { href: "/", label: "gallery", match: (p: string) => p === "/" },
  {
    href: "/generate",
    label: "generate",
    match: (p: string) => p.startsWith("/generate"),
  },
  {
    href: "/results",
    label: "output",
    match: (p: string) => p.startsWith("/results"),
  },
];

export function Header() {
  const pathname = usePathname();

  return (
    <header
      className="sticky top-0 z-50 flex items-center justify-between h-12 px-6 border-b border-border backdrop-blur-md"
      style={{ background: "rgba(10,12,16,0.92)" }}
    >
      {/* Logo */}
      <Link href="/" className="flex items-center gap-2 group">
        <div className="w-5 h-5 border-2 border-primary rounded-[2px] flex items-center justify-center">
          <span className="font-mono text-[10px] font-bold text-primary leading-none">
            BV
          </span>
        </div>
        <span
          className="font-mono text-xs font-semibold text-text"
          style={{ letterSpacing: "0.04em" }}
        >
          beat_visuals
        </span>
      </Link>

      {/* Nav */}
      <nav className="flex gap-0.5">
        {navLinks.map(({ href, label, match }) => {
          const isActive = match(pathname);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "font-mono text-[11px] uppercase px-3.5 py-1.5 rounded-sm border transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50",
                isActive
                  ? "border-primary bg-primary/15 text-primary"
                  : "border-border bg-transparent text-text-muted hover:border-border-light hover:text-text"
              )}
              style={{ letterSpacing: "0.04em" }}
            >
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Status — hidden on mobile to keep logo + nav breathing room */}
      <div className="hidden sm:flex items-center gap-3">
        <div className="flex items-center gap-1">
          <span
            className="w-1.5 h-1.5 rounded-full bg-green"
            style={{ boxShadow: "0 0 6px rgba(0,255,136,0.6)" }}
          />
          <MonoLabel color="var(--color-text-muted)">api</MonoLabel>
        </div>
        <MonoLabel>v0.1.0</MonoLabel>
      </div>
    </header>
  );
}
