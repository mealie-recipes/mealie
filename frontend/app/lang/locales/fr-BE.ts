export default defineI18nLocale(async () => {
  const { fr: $vuetify } = await import("vuetify/locale");
  const { default: frBE } = await import("../messages/fr-BE.json");
  return {
    ...frBE,
    $vuetify,
  };
});
