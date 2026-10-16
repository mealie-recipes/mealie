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
}

export const RADIUS_PX: Record<string, string> = {
  sharp: "0px",
  soft: "4px",
  round: "16px",
};

/** Applies the non-color design tokens via CSS custom property + class, so every component
 * that reads them (see assets/main.css) picks up the change without a reload. No-op during SSR. */
export function applyDesignTokens(theme: Pick<ThemeConfig, "borderRadius" | "cardStyle"> | undefined) {
  if (import.meta.server) {
    return;
  }

  document.documentElement.style.setProperty("--mealie-radius", RADIUS_PX[theme?.borderRadius ?? "soft"] ?? RADIUS_PX.soft!);
  document.documentElement.classList.toggle("theme-flat-cards", theme?.cardStyle === "flat");
}
