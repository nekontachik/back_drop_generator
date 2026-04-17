import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  color?: string;
}

const DEFAULT_COLOR = "#00AAFF";

const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, color = DEFAULT_COLOR, style, children, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(
          "inline-flex items-center font-mono text-[10px] tracking-wider px-2 py-0.5 rounded-sm border",
          className
        )}
        style={{
          color,
          borderColor: `${color}40`,
          backgroundColor: `${color}10`,
          ...style,
        }}
        {...props}
      >
        {children}
      </span>
    );
  }
);
Badge.displayName = "Badge";

export { Badge };
