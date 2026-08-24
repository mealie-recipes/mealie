export default defineI18nLocale(async () => {
  const { hr: $vuetify } = await import("vuetify/locale");
  const { default: hrHR } = await import("../messages/hr-HR.json");
  return {
    ...hrHR,
    $vuetify,
  };
});
