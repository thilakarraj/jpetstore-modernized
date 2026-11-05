import { forwardRef, type SelectHTMLAttributes } from "react";
import { cn } from "@/utils/cn";

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, id, children, ...props }, ref) => {
    const selectId = id ?? props.name;
    return (
      <div className="space-y-1.5">
        {label ? (
          <label htmlFor={selectId} className="text-sm font-medium text-foreground">
            {label}
          </label>
        ) : null}
        <select
          ref={ref}
          id={selectId}
          className={cn(
            "flex h-11 w-full cursor-pointer rounded-lg border border-input-border bg-input px-3 text-sm text-foreground focus-visible:border-ring disabled:opacity-50",
            error && "border-error",
            className,
          )}
          {...props}
        >
          {children}
        </select>
        {error ? <p className="text-xs text-error">{error}</p> : null}
      </div>
    );
  },
);
Select.displayName = "Select";
