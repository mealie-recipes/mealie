export default defineI18nLocale(async () => {
  const { lt: $vuetify } = await import("vuetify/locale");
  const { default: ltLT } = await import("../messages/lt-LT.json");
  return {
    ...ltLT,
    $vuetify,
  };
});
