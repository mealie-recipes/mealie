export default defineI18nLocale(async () => {
  const { sv: $vuetify } = await import("vuetify/locale");
  const { default: svSE } = await import("../messages/sv-SE.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/sv-SE.json",
  );
  return {
    ...svSE,
    "unit-names": unitNames,
    $vuetify,
  };
});
