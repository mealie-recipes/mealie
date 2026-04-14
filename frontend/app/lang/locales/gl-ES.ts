export default defineI18nLocale(async () => {
  const { es: $vuetify } = await import("vuetify/locale");
  const { default: glES } = await import("../messages/gl-ES.json");
  return {
    ...glES,
    $vuetify,
  };
});
