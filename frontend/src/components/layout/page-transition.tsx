"use client";

import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

export function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [visible, setVisible] = useState(false);
  const prevRef = useRef(pathname);

  // Fade in on first mount
  useEffect(() => {
    setVisible(true);
  }, []);

  // Restart animation on route change
  useEffect(() => {
    if (pathname === prevRef.current) return;
    prevRef.current = pathname;
    setVisible(false);
    const raf = requestAnimationFrame(() => {
      requestAnimationFrame(() => setVisible(true));
    });
    return () => cancelAnimationFrame(raf);
  }, [pathname]);

  return (
    <div
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(6px)",
        transition: "opacity 220ms ease-out, transform 220ms ease-out",
      }}
    >
      {children}
    </div>
  );
}
