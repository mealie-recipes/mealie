export default defineI18nLocale(async () => {
  const { ja: $vuetify } = await import("vuetify/locale");
  const { default: jaJP } = await import("../messages/ja-JP.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/ja-JP.json",
  );
  return {
    ...jaJP,
    "unit-names": unitNames,
    $vuetify,
  };
});
