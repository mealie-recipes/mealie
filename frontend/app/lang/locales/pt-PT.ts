export default defineI18nLocale(async () => {
  const { pt: $vuetify } = await import("vuetify/locale");
  const { default: ptPT } = await import("../messages/pt-PT.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/pt-PT.json",
  );
  return {
    ...ptPT,
    "unit-names": unitNames,
    $vuetify,
  };
});
