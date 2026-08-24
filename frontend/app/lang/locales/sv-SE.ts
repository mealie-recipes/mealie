export default defineI18nLocale(async () => {
  const { sv: $vuetify } = await import("vuetify/locale");
  const { default: svSE } = await import("../messages/sv-SE.json");
  return {
    ...svSE,
    $vuetify,
  };
});
