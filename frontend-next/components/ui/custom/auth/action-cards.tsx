"use client";

import * as React from "react";
import { ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

const ActionCardGroupContext = React.createContext<
  | {
      value?: string;
      onValueChange?: (value: string) => void;
    }
  | undefined
>(undefined);

interface ActionCardGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: string;
  onValueChange?: (value: string) => void;
}

export const ActionCardGroup = React.forwardRef<
  HTMLDivElement,
  ActionCardGroupProps
>(({ value, onValueChange, className, children, ...props }, ref) => {
  return (
    <ActionCardGroupContext.Provider value={{ value, onValueChange }}>
      <div
        ref={ref}
        // We keep role="radiogroup" because semantically it is still a single-select group,
        // even if visually it looks like cards. This helps screen readers understand the relationship.
        role="radiogroup"
        className={cn(
          "grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-2xl",
          className
        )}
        {...props}
      >
        {children}
      </div>
    </ActionCardGroupContext.Provider>
  );
});
ActionCardGroup.displayName = "ActionCardGroup";

interface ActionCardProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  value: string;
  icon: React.ReactNode;
  title: string;
  description: string;
}

export const ActionCard = React.forwardRef<HTMLButtonElement, ActionCardProps>(
  ({ value, icon, title, description, className, ...props }, ref) => {
    const context = React.useContext(ActionCardGroupContext);
    const isSelected = context?.value === value;

    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
      context?.onValueChange?.(value);
      props.onClick?.(e);
    };

    return (
      <button
        ref={ref}
        type="button"
        role="radio"
        aria-checked={isSelected}
        data-state={isSelected ? "checked" : "unchecked"}
        onClick={handleClick}
        className={cn(
          "group relative flex flex-col items-center justify-center gap-6 h-64 md:h-72 rounded-3xl border-2 transition-all duration-300 cursor-pointer overflow-hidden",
          // Base styles
          "border-zinc-800 bg-zinc-900/40 hover:bg-zinc-900/60",
          // Selected or Hover styles
          "hover:border-primary hover:bg-zinc-900/80 hover:shadow-[0_0_30px_-5px_rgba(249,115,22,0.3)] hover:scale-[1.02]",
          "data-[state=checked]:border-primary data-[state=checked]:bg-zinc-900/80 data-[state=checked]:shadow-[0_0_30px_-5px_rgba(249,115,22,0.3)] data-[state=checked]:scale-[1.02]",
          className
        )}
        {...props}
      >
        <div
          className={cn(
            "p-6 rounded-2xl transition-all duration-300",
            "bg-zinc-800 text-zinc-400",
            "group-hover:bg-primary group-hover:text-white",
            "group-data-[state=checked]:bg-primary group-data-[state=checked]:text-white"
          )}
        >
          {icon}
        </div>
        <div className="text-center space-y-2 px-4">
          <h3 className="text-2xl font-bold text-white">{title}</h3>
          <p className="text-zinc-400 text-sm max-w-[200px]">{description}</p>
        </div>
      </button>
    );
  }
);
ActionCard.displayName = "ActionCard";
