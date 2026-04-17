import * as React from "react";
import { cn } from "@/lib/utils";

export interface MonoLabelProps
  extends React.HTMLAttributes<HTMLSpanElement> {
  color?: string;
}

const MonoLabel = React.forwardRef<HTMLSpanElement, MonoLabelProps>(
  ({ className, color, style, children, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(
          "font-mono text-[10px] uppercase tracking-widest text-text-dim",
          className
        )}
        style={color ? { color, ...style } : style}
        {...props}
      >
        {children}
      </span>
    );
  }
);
MonoLabel.displayName = "MonoLabel";

export { MonoLabel };
