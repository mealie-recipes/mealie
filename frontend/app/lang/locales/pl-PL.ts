export default defineI18nLocale(async () => {
  const { pl: $vuetify } = await import("vuetify/locale");
  const { default: plPL } = await import("../messages/pl-PL.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/pl-PL.json",
  );
  return {
    ...plPL,
    "unit-names": unitNames,
    $vuetify,
  };
});
