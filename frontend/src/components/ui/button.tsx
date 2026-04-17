import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-[#050810] hover:bg-primary-bright active:bg-primary-muted",
        outline:
          "border border-primary bg-transparent text-primary hover:bg-primary/10 active:bg-primary/20",
        ghost:
          "bg-transparent text-text-muted hover:bg-primary/10 hover:text-primary active:bg-primary/20",
        violet:
          "bg-violet text-white hover:bg-violet-light active:bg-violet-dark",
        hardware:
          "font-mono uppercase tracking-wider text-[11px] border border-border bg-transparent text-text-muted hover:border-border-light hover:text-text aria-pressed:border-primary aria-pressed:bg-primary/15 aria-pressed:text-primary data-[active=true]:border-primary data-[active=true]:bg-primary/15 data-[active=true]:text-primary",
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
