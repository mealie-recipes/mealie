export default defineI18nLocale(async () => {
  const { ru: $vuetify } = await import("vuetify/locale");
  const { default: ruRU } = await import("../messages/ru-RU.json");
  return {
    ...ruRU,
    $vuetify,
  };
});
