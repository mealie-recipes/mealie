// File was already correctly named
export default defineI18nLocale(async () => {
  const { en: $vuetify } = await import("vuetify/locale");
  const { default: enUS } = await import("../messages/en-US.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/en-US.json",
  );
  return {
    ...enUS,
    "unit-names": unitNames,
    $vuetify,
  };
});
