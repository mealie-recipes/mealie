export default defineI18nLocale(async () => {
  const { de: $vuetify } = await import("vuetify/locale");
  const { default: deDE } = await import("../messages/de-DE.json");
  return {
    ...deDE,
    $vuetify,
  };
});
