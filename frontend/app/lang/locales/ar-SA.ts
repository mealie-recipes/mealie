export default defineI18nLocale(async () => {
  const { ar: $vuetify } = await import("vuetify/locale");
  const { default: arSA } = await import("../messages/ar-SA.json");
  return {
    ...arSA,
    $vuetify,
  };
});
