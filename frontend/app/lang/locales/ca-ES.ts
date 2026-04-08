export default defineI18nLocale(async () => {
  const { ca: $vuetify } = await import("vuetify/locale");
  const { default: caES } = await import("../messages/ca-ES.json");
  return {
    ...caES,
    $vuetify,
  };
});
