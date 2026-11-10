export default defineI18nLocale(async () => {
  const { fi: $vuetify } = await import("vuetify/locale");
  const { default: fiFI } = await import("../messages/fi-FI.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/fi-FI.json",
  );
  return {
    ...fiFI,
    "unit-names": unitNames,
    $vuetify,
  };
});
