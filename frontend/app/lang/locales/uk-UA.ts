export default defineI18nLocale(async () => {
  const { uk: $vuetify } = await import("vuetify/locale");
  const { default: ukUA } = await import("../messages/uk-UA.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/uk-UA.json",
  );
  return {
    ...ukUA,
    "unit-names": unitNames,
    $vuetify,
  };
});
