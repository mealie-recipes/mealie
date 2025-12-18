"use client";

import { useCallback, useState } from "react";
import { Check, Copy, Eye, EyeOff } from "lucide-react";

import { cn } from "@/lib/utils";

interface CredentialRowProps extends React.ComponentProps<"div"> {
  label: string;
  value: string;
  isPassword?: boolean;
}

function CredentialRow({
  label,
  value,
  isPassword = false,
  className,
  ...props
}: CredentialRowProps) {
  const [copied, setCopied] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy to clipboard:", err);
    }
  }, [value]);

  return (
    <div
      data-slot="credential-row"
      className={cn(
        "ring-foreground/10 bg-input/20 dark:bg-input/30 border-input hover:bg-input/30 dark:hover:bg-input/40 flex items-center justify-between gap-3 rounded-md border px-3 py-2 transition-colors ring-1",
        className
      )}
      {...props}
    >
      <div className="flex min-w-0 flex-col gap-1">
        <span className="text-[10px]/tight font-semibold uppercase tracking-wider text-muted-foreground">
          {label}
        </span>
        <code className="truncate font-mono text-xs/relaxed text-foreground">
          {isPassword && !showPassword ? (
            <span className="tracking-widest">••••••••••</span>
          ) : (
            value
          )}
        </code>
      </div>
      <div className="flex items-center gap-1">
        {isPassword && value && (
          <button
            onClick={() => setShowPassword(!showPassword)}
            className={cn(
              "text-muted-foreground hover:text-foreground focus-visible:border-ring focus-visible:ring-ring/30 shrink-0 rounded-md border border-transparent p-1 transition-colors focus-visible:ring-[2px] outline-none"
            )}
            title={showPassword ? "Hide password" : "Show password"}
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
          </button>
        )}
        <button
          onClick={handleCopy}
          className={cn(
            "text-muted-foreground hover:text-foreground focus-visible:border-ring focus-visible:ring-ring/30 shrink-0 rounded-md border border-transparent p-1 transition-colors focus-visible:ring-[2px] outline-none"
          )}
          title={copied ? "Copied!" : "Copy to clipboard"}
          aria-label={`Copy ${label}`}
        >
          {copied ? (
            <Check size={14} className="text-primary" />
          ) : (
            <Copy size={14} />
          )}
        </button>
      </div>
    </div>
  );
}

export { CredentialRow };
