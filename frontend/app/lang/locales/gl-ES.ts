export default defineI18nLocale(async () => {
  const { es: $vuetify } = await import("vuetify/locale");
  const { default: glES } = await import("../messages/gl-ES.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/gl-ES.json",
  );
  return {
    ...glES,
    "unit-names": unitNames,
    $vuetify,
  };
});
