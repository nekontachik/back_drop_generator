import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-lg font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-amber disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "bg-accent-amber text-black hover:bg-accent-amber-light active:bg-accent-amber-dark",
        outline:
          "border border-white/20 bg-transparent text-white hover:bg-white/5 active:bg-white/10",
        ghost:
          "bg-transparent text-white hover:bg-white/5 active:bg-white/10",
        magenta:
          "bg-accent-magenta text-white hover:bg-accent-magenta-light active:bg-accent-magenta-dark",
      },
      size: {
        sm: "h-8 px-3 text-sm",
        default: "h-10 px-5 text-sm",
        lg: "h-12 px-6 text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
