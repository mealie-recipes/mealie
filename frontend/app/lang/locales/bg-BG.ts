export default defineI18nLocale(async () => {
  const { bg: $vuetify } = await import("vuetify/locale");
  const { default: bgBG } = await import("../messages/bg-BG.json");
  return {
    ...bgBG,
    $vuetify,
  };
});
