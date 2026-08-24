export default defineI18nLocale(async () => {
  const { pt: $vuetify } = await import("vuetify/locale");
  const { default: ptPT } = await import("../messages/pt-PT.json");
  return {
    ...ptPT,
    $vuetify,
  };
});
