import { useDark } from "@vueuse/core";

export default defineNuxtPlugin((nuxtApp) => {
  const isDark = useDark({
    onChanged: (v) => {
      console.log(`changing theme to ${v ? "dark" : "light"} using @vueuse/useDark`);
      const $vuetify = nuxtApp.vueApp.$nuxt.$vuetify;
      if ($vuetify)
        $vuetify.theme.global.name.value = v ? "dark" : "light";
    },
  });

  nuxtApp.hook("vuetify:ready", (vuetify) => {
    vuetify.theme.global.name.value = isDark.value ? "dark" : "light";
  });

  return {
    provide: {},
  };
});
