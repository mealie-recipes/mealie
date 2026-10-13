import { withReadableOn } from "~/lib/theme/readable-on";

// filled components in these colours get a label colour that meets 4.5:1 against them
const ON_COLORS = ["primary", "accent", "secondary", "success", "info", "warning", "error"] as const;

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
}

let __cachedTheme: ThemeConfig | undefined;

async function fetchTheme(): Promise<ThemeConfig | undefined> {
  const route = "/api/app/about/theme";

  try {
    const response = await fetch(route);
    const data = await response.json();
    return data as ThemeConfig;
  }
  catch {
    return undefined;
  }
}

export default defineNuxtPlugin(async (nuxtApp) => {
  nuxtApp.hook("vuetify:before-create", async ({ vuetifyOptions }) => {
    let theme = __cachedTheme;
    if (!theme) {
      theme = await fetchTheme();
      __cachedTheme = theme;
    }
    vuetifyOptions.theme = {
      defaultTheme: nuxtApp.$config.public.useDark ? "dark" : "light",
      variations: {
        colors: ["primary", "accent", "secondary", "success", "info", "warning", "error", "background"],
        lighten: 3,
        darken: 3,
      },
      themes: {
        light: {
          dark: false,
          colors: withReadableOn({
            primary: theme?.lightPrimary ?? "#C4502A",
            accent: theme?.lightAccent ?? "#007A99",
            secondary: theme?.lightSecondary ?? "#973542",
            success: theme?.lightSuccess ?? "#2A7531",
            info: theme?.lightInfo ?? "#1565C0",
            warning: theme?.lightWarning ?? "#A84B0A",
            error: theme?.lightError ?? "#B3261E",
            background: "#FAF9F7",
            surface: "#FFFFFF",
          }, ON_COLORS),
        },
        dark: {
          dark: true,
          colors: withReadableOn({
            primary: theme?.darkPrimary ?? "#E0683C",
            accent: theme?.darkAccent ?? "#007A99",
            secondary: theme?.darkSecondary ?? "#E08A73",
            success: theme?.darkSuccess ?? "#4CAF50",
            info: theme?.darkInfo ?? "#5E9BD1",
            warning: theme?.darkWarning ?? "#FF6D00",
            error: theme?.darkError ?? "#F2706C",
            background: "#161513",
            surface: "#1F1E1C",
          }, ON_COLORS),
        },
      },
    };
  });
});
