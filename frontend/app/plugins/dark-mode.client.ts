import { useDark } from "@vueuse/core";

export default defineNuxtPlugin((nuxtApp) => {
  const isDark = useDark({
    onChanged: (v) => {
      console.log(`changing theme to ${v ? "dark" : "light"} using @vueuse/useDark`);
      const $vuetify = nuxtApp.vueApp.$nuxt.$vuetify;
      if ($vuetify)
        $vuetify.theme.toggle();
    },
  });

  nuxtApp.hook("vuetify:ready", (vuetify) => {
    vuetify.theme.change(isDark.value ? "dark" : "light");
  });

  return {
    provide: {},
  };
});
