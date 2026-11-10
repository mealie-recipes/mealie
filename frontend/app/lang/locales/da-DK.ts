export default defineI18nLocale(async () => {
  const { da: $vuetify } = await import("vuetify/locale");
  const { default: daDK } = await import("../messages/da-DK.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/da-DK.json",
  );
  return {
    ...daDK,
    "unit-names": unitNames,
    $vuetify,
  };
});
