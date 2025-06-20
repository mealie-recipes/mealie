export default defineI18nLocale(async () => {
  const { nl: $vuetify } = await import("vuetify/locale");
  const { default: nlNL } = await import("../messages/nl-NL.json");
  return {
    ...nlNL,
    $vuetify,
  };
});
