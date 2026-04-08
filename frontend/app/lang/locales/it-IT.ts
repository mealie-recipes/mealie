export default defineI18nLocale(async () => {
  const { it: $vuetify } = await import("vuetify/locale");
  const { default: itIT } = await import("../messages/it-IT.json");
  return {
    ...itIT,
    $vuetify,
  };
});
