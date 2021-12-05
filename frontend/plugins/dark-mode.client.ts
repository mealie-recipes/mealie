import { useDark } from "@vueuse/core";

export default ({ $vuetify }: any) => {
  const isDark = useDark();
  console.log("isDark Plugin", isDark);

  if (isDark.value) {
    $vuetify.theme.dark = true;
  } else {
    $vuetify.theme.dark = false;
  }
};
