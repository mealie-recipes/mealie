export default defineI18nLocale(async () => {
  const { hr: $vuetify } = await import("vuetify/locale");
  const { default: hrHR } = await import("../messages/hr-HR.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/hr-HR.json",
  );
  return {
    ...hrHR,
    "unit-names": unitNames,
    $vuetify,
  };
});
