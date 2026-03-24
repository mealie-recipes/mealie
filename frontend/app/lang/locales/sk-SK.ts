export default defineI18nLocale(async () => {
  const { sk: $vuetify } = await import("vuetify/locale");
  const { default: skSK } = await import("../messages/sk-SK.json");
  return {
    ...skSK,
    $vuetify,
  };
});
