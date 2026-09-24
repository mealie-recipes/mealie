export default defineI18nLocale(async () => {
  const { lv: $vuetify } = await import("vuetify/locale");
  const { default: lvLV } = await import("../messages/lv-LV.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/lv-LV.json",
  );
  return {
    ...lvLV,
    "unit-names": unitNames,
    $vuetify,
  };
});
