export default defineI18nLocale(async () => {
  const { sl: $vuetify } = await import("vuetify/locale");
  const { default: slSI } = await import("../messages/sl-SI.json");
  return {
    ...slSI,
    $vuetify,
  };
});
