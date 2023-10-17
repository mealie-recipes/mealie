import { Plugin } from "@nuxt/types"
import { useDark } from "@vueuse/core";

const darkModePlugin: Plugin = ({ $vuetify }, _) => {
  const isDark = useDark();

  // Vuetify metadata is bugged and doesn't render dark mode fully when called immediately
  // Adding a delay fixes this problem
  // https://stackoverflow.com/questions/69399797/vuetify-darkmode-colors-wrong-after-page-reload
  setTimeout(() => { $vuetify.theme.dark = isDark.value; }, 200);
};

export default darkModePlugin;
