export default defineI18nLocale(async () => {
  const { af: $vuetify } = await import("vuetify/locale");
  const { default: afZA } = await import("../messages/af-ZA.json");
  return {
    ...afZA,
    $vuetify,
  };
});
