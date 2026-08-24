export default defineI18nLocale(async () => {
  const { fr: $vuetify } = await import("vuetify/locale");
  const { default: frCA } = await import("../messages/fr-CA.json");
  return {
    ...frCA,
    $vuetify,
  };
});
