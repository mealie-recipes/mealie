export default defineI18nLocale(async () => {
  const { en: $vuetify } = await import("vuetify/locale");
  const { default: srSP } = await import("../messages/sr-SP.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/sr-SP.json",
  );
  return {
    ...srSP,
    "unit-names": unitNames,
    $vuetify,
  };
});
