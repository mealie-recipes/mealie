import { applyDesignTokens, type ThemeConfig } from "~/composables/use-theme-design";

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
  // Pre-warm the cache before Vuetify is created: `vuetify:before-create` runs
  // synchronously, so an await inside it would race Vuetify reading vuetifyOptions.theme
  // and lose - leaving every cold load on fallback colors regardless of server config.
  if (!__cachedTheme) {
    __cachedTheme = await fetchTheme();
  }

  applyDesignTokens(__cachedTheme);

  nuxtApp.hook("vuetify:before-create", ({ vuetifyOptions }) => {
    const theme = __cachedTheme;
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
          colors: {
            primary: theme?.lightPrimary ?? "#A65F1B",
            accent: theme?.lightAccent ?? "#007A99",
            secondary: theme?.lightSecondary ?? "#973542",
            success: theme?.lightSuccess ?? "#43A047",
            info: theme?.lightInfo ?? "#1976d2",
            warning: theme?.lightWarning ?? "#FF6D00",
            error: theme?.lightError ?? "#EF5350",
          },
        },
        dark: {
          dark: true,
          colors: {
            primary: theme?.darkPrimary ?? "#A65F1B",
            accent: theme?.darkAccent ?? "#007A99",
            secondary: theme?.darkSecondary ?? "#973542",
            success: theme?.darkSuccess ?? "#43A047",
            info: theme?.darkInfo ?? "#1976d2",
            warning: theme?.darkWarning ?? "#FF6D00",
            error: theme?.darkError ?? "#EF5350",
            background: "#1E1E1E",
            surface: "#1E1E1E",
          },
        },
      },
    };
  });
});
