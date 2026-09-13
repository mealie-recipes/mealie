export default defineI18nLocale(async () => {
  const { es: $vuetify } = await import("vuetify/locale");
  const { default: esES } = await import("../messages/es-ES.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/es-ES.json",
  );
  return {
    ...esES,
    "unit-names": unitNames,
    $vuetify,
  };
});
