export default defineI18nLocale(async () => {
  const { uk: $vuetify } = await import("vuetify/locale");
  const { default: ukUA } = await import("../messages/uk-UA.json");
  return {
    ...ukUA,
    $vuetify,
  };
});
