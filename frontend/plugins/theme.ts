import { Plugin } from "@nuxt/types"

const themePlugin: Plugin = ({ $vuetify, $config }) => {
  $vuetify.theme.themes = $config.themes as typeof $vuetify.theme.themes

  if ($config.useDark) {
    $vuetify.theme.dark = true;
  }
};

export default themePlugin;
