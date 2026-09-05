export default defineI18nLocale(async () => {
  const { sk: $vuetify } = await import("vuetify/locale");
  const { default: skSK } = await import("../messages/sk-SK.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/sk-SK.json",
  );
  return {
    ...skSK,
    "unit-names": unitNames,
    $vuetify,
  };
});
