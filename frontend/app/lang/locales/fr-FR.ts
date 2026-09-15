export default defineI18nLocale(async () => {
  const { fr: $vuetify } = await import("vuetify/locale");
  const { default: frFR } = await import("../messages/fr-FR.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/fr-FR.json",
  );
  return {
    ...frFR,
    "unit-names": unitNames,
    $vuetify,
  };
});
