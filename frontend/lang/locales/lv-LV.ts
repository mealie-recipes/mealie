export default defineI18nLocale(async () => {
  const { lv: $vuetify } = await import("vuetify/locale");
  const { default: lvLV } = await import("../messages/lv-LV.json");
  return {
    ...lvLV,
    $vuetify,
  };
});
