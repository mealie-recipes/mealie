export default defineI18nLocale(async () => {
  const { af: $vuetify } = await import("vuetify/locale");
  const { default: afZA } = await import("../messages/af-ZA.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/af-ZA.json",
  );
  return {
    ...afZA,
    "unit-names": unitNames,
    $vuetify,
  };
});
