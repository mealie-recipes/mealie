export default defineI18nLocale(async () => {
  const { et: $vuetify } = await import("vuetify/locale");
  const { default: etEE } = await import("../messages/et-EE.json");
  return {
    ...etEE,
    $vuetify,
  };
});
