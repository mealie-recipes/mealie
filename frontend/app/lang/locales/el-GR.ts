export default defineI18nLocale(async () => {
  const { el: $vuetify } = await import("vuetify/locale");
  const { default: elGR } = await import("../messages/el-GR.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/el-GR.json",
  );
  return {
    ...elGR,
    "unit-names": unitNames,
    $vuetify,
  };
});
