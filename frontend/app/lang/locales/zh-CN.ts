export default defineI18nLocale(async () => {
  const { zhHans: $vuetify } = await import("vuetify/locale");
  const { default: zhCN } = await import("../messages/zh-CN.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/zh-CN.json",
  );
  return {
    ...zhCN,
    "unit-names": unitNames,
    $vuetify,
  };
});
