export interface ThemeConfig {
  lightPrimary: string;
  lightAccent: string;
  lightSecondary: string;
  lightSuccess: string;
  lightInfo: string;
  lightWarning: string;
  lightError: string;
  darkPrimary: string;
  darkAccent: string;
  darkSecondary: string;
  darkSuccess: string;
  darkInfo: string;
  darkWarning: string;
  darkError: string;
  borderRadius?: "sharp" | "soft" | "round";
  cardStyle?: "elevated" | "flat";
  fontFamily?: "sans" | "rounded" | "serif" | "mono";
  fontSize?: "small" | "medium" | "large";
}

export const RADIUS_PX: Record<string, string> = {
  sharp: "0px",
  soft: "4px",
  round: "16px",
};

// System font stacks only - never a downloaded webfont, so picking one never adds a network
// request. "sans" matches the stack the app already fell back to before this feature existed,
// so it's a no-op default.
export const FONT_STACKS: Record<string, string> = {
  sans: "system-ui, -apple-system, \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif",
  rounded: "ui-rounded, \"SF Pro Rounded\", \"Comic Neue\", Verdana, sans-serif",
  serif: "ui-serif, Georgia, \"Times New Roman\", Times, serif",
  mono: "ui-monospace, \"SF Mono\", \"Cascadia Code\", \"Fira Code\", Consolas, Menlo, monospace",
};

export const FONT_SIZE_PX: Record<string, string> = {
  small: "14px",
  medium: "16px",
  large: "18px",
};

/** Applies the non-color design tokens via CSS custom property + class, so every component
 * that reads them (see assets/main.css) picks up the change without a reload. No-op during SSR. */
export function applyDesignTokens(
  theme: Pick<ThemeConfig, "borderRadius" | "cardStyle" | "fontFamily" | "fontSize"> | undefined,
) {
  if (import.meta.server) {
    return;
  }

  const root = document.documentElement.style;
  root.setProperty("--mealie-radius", RADIUS_PX[theme?.borderRadius ?? "soft"] ?? RADIUS_PX.soft!);
  root.setProperty("--mealie-font-family", FONT_STACKS[theme?.fontFamily ?? "sans"] ?? FONT_STACKS.sans!);
  root.setProperty("--mealie-font-size", FONT_SIZE_PX[theme?.fontSize ?? "medium"] ?? FONT_SIZE_PX.medium!);
  document.documentElement.classList.toggle("theme-flat-cards", theme?.cardStyle === "flat");
}
