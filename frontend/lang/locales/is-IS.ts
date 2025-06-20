export default defineI18nLocale(async () => {
  const { en: $vuetify } = await import("vuetify/locale");
  const { default: isIS } = await import("../messages/is-IS.json");
  return {
    ...isIS,
    $vuetify,
  };
});
