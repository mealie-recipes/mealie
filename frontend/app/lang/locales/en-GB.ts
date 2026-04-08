export default defineI18nLocale(async () => {
  const { en: $vuetify } = await import("vuetify/locale");
  const { default: enGB } = await import("../messages/en-GB.json");
  return {
    ...enGB,
    $vuetify,
  };
});
