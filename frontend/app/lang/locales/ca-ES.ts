export default defineI18nLocale(async () => {
  const { ca: $vuetify } = await import("vuetify/locale");
  const { default: caES } = await import("../messages/ca-ES.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/ca-ES.json",
  );
  return {
    ...caES,
    "unit-names": unitNames,
    $vuetify,
  };
});
