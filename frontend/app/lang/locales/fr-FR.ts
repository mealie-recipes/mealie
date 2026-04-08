export default defineI18nLocale(async () => {
  const { fr: $vuetify } = await import("vuetify/locale");
  const { default: frFR } = await import("../messages/fr-FR.json");
  return {
    ...frFR,
    $vuetify,
  };
});
