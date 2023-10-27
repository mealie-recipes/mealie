import { Plugin } from "@nuxt/types";

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
  } catch (error) {
    return undefined;
  }
}

const themePlugin: Plugin =  async ({ $vuetify, $config }) => {
  let theme = __cachedTheme;
  if (!theme) {
    theme = await fetchTheme();
    __cachedTheme = theme;
  }

  if (theme) {
    $vuetify.theme.themes.light.primary = theme.lightPrimary;
    $vuetify.theme.themes.light.accent = theme.lightAccent;
    $vuetify.theme.themes.light.secondary = theme.lightSecondary;
    $vuetify.theme.themes.light.success = theme.lightSuccess;
    $vuetify.theme.themes.light.info = theme.lightInfo;
    $vuetify.theme.themes.light.warning = theme.lightWarning;
    $vuetify.theme.themes.light.error = theme.lightError;

    $vuetify.theme.themes.dark.primary = theme.darkPrimary;
    $vuetify.theme.themes.dark.accent = theme.darkAccent;
    $vuetify.theme.themes.dark.secondary = theme.darkSecondary;
    $vuetify.theme.themes.dark.success = theme.darkSuccess;
    $vuetify.theme.themes.dark.info = theme.darkInfo;
    $vuetify.theme.themes.dark.warning = theme.darkWarning;
    $vuetify.theme.themes.dark.error = theme.darkError;
  }

  if ($config.useDark) {
    $vuetify.theme.dark = true;
  }
};

export default themePlugin;
