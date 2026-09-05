export default defineI18nLocale(async () => {
  const { et: $vuetify } = await import("vuetify/locale");
  const { default: etEE } = await import("../messages/et-EE.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/et-EE.json",
  );
  return {
    ...etEE,
    "unit-names": unitNames,
    $vuetify,
  };
});
