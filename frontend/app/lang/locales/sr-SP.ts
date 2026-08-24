export default defineI18nLocale(async () => {
  const { en: $vuetify } = await import("vuetify/locale");
  const { default: srSP } = await import("../messages/sr-SP.json");
  return {
    ...srSP,
    $vuetify,
  };
});
