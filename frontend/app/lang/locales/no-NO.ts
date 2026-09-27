export default defineI18nLocale(async () => {
  const { no: $vuetify } = await import("vuetify/locale");
  const { default: noNO } = await import("../messages/no-NO.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/no-NO.json",
  );
  return {
    ...noNO,
    "unit-names": unitNames,
    $vuetify,
  };
});
