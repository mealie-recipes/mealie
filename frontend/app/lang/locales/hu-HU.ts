export default defineI18nLocale(async () => {
  const { hu: $vuetify } = await import("vuetify/locale");
  const { default: huHU } = await import("../messages/hu-HU.json");
  return {
    ...huHU,
    $vuetify,
  };
});
