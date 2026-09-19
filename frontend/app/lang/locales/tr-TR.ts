export default defineI18nLocale(async () => {
  const { tr: $vuetify } = await import("vuetify/locale");
  const { default: trTR } = await import("../messages/tr-TR.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/tr-TR.json",
  );
  return {
    ...trTR,
    "unit-names": unitNames,
    $vuetify,
  };
});
