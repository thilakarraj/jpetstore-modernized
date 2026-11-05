import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/utils/cn";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, id, ...props }, ref) => {
    const inputId = id ?? props.name;
    return (
      <div className="space-y-1.5">
        {label ? (
          <label htmlFor={inputId} className="text-sm font-medium text-foreground">
            {label}
          </label>
        ) : null}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            "flex h-11 w-full rounded-lg border border-input-border bg-input px-3 py-2 text-sm text-foreground transition-colors placeholder:text-muted-foreground focus-visible:border-ring disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-error",
            className,
          )}
          aria-invalid={error ? true : undefined}
          {...props}
        />
        {error ? (
          <p className="text-xs text-error" role="alert">
            {error}
          </p>
        ) : null}
      </div>
    );
  },
);
Input.displayName = "Input";
