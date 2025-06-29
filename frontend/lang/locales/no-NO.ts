export default defineI18nLocale(async () => {
  const { no: $vuetify } = await import("vuetify/locale");
  const { default: noNO } = await import("../messages/no-NO.json");
  return {
    ...noNO,
    $vuetify,
  };
});
