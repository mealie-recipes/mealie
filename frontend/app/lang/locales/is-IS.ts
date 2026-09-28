export default defineI18nLocale(async () => {
  const { en: $vuetify } = await import("vuetify/locale");
  const { default: isIS } = await import("../messages/is-IS.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/is-IS.json",
  );
  return {
    ...isIS,
    "unit-names": unitNames,
    $vuetify,
  };
});
