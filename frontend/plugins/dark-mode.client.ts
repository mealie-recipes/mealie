import { Plugin } from "@nuxt/types"
import { useDark } from "@vueuse/core";

const darkModePlugin: Plugin = ({ $vuetify }, _) => {
  const isDark = useDark();

  $vuetify.theme.dark = isDark.value;
};

export default darkModePlugin;
