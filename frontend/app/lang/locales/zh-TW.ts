export default defineI18nLocale(async () => {
  const { zhHant: $vuetify } = await import("vuetify/locale");
  const { default: zhTW } = await import("../messages/zh-TW.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/zh-TW.json",
  );
  return {
    ...zhTW,
    "unit-names": unitNames,
    $vuetify,
  };
});
