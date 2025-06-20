export default defineI18nLocale(async () => {
  const { tr: $vuetify } = await import("vuetify/locale");
  const { default: trTR } = await import("../messages/tr-TR.json");
  return {
    ...trTR,
    $vuetify,
  };
});
