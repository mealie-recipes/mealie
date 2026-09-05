export default defineI18nLocale(async () => {
  const { fr: $vuetify } = await import("vuetify/locale");
  const { default: frBE } = await import("../messages/fr-BE.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/fr-BE.json",
  );
  return {
    ...frBE,
    "unit-names": unitNames,
    $vuetify,
  };
});
