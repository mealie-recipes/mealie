export default defineI18nLocale(async () => {
  const { da: $vuetify } = await import("vuetify/locale");
  const { default: daDK } = await import("../messages/da-DK.json");
  return {
    ...daDK,
    $vuetify,
  };
});
