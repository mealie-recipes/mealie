export default defineI18nLocale(async () => {
  const { fi: $vuetify } = await import("vuetify/locale");
  const { default: fiFI } = await import("../messages/fi-FI.json");
  return {
    ...fiFI,
    $vuetify,
  };
});
