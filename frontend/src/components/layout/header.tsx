"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navLinks = [
  { href: "/", label: "Gallery" },
  { href: "/generate", label: "Generate" },
];

export function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 bg-surface/80 backdrop-blur-md border-b border-white/5">
      <div className="max-w-7xl mx-auto px-6 lg:px-12 h-14 flex items-center justify-between">
        {/* Logo */}
        <Link
          href="/"
          className="text-accent-amber font-display font-bold text-xl tracking-tight hover:text-accent-amber-light transition-colors"
        >
          Beat Visuals
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-6">
          {navLinks.map(({ href, label }) => {
            const isActive =
              href === "/" ? pathname === "/" : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "text-sm font-medium transition-colors relative pb-0.5",
                  isActive
                    ? "text-white after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-accent-amber after:rounded-full"
                    : "text-white/60 hover:text-white"
                )}
              >
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
