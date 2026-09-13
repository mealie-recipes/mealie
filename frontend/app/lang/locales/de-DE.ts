export default defineI18nLocale(async () => {
  const { de: $vuetify } = await import("vuetify/locale");
  const { default: deDE } = await import("../messages/de-DE.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/de-DE.json",
  );
  return {
    ...deDE,
    "unit-names": unitNames,
    $vuetify,
  };
});
