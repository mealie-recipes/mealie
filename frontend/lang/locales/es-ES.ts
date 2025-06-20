export default defineI18nLocale(async () => {
  const { es: $vuetify } = await import("vuetify/locale");
  const { default: esES } = await import("../messages/es-ES.json");
  return {
    ...esES,
    $vuetify,
  };
});
