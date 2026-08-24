export default defineI18nLocale(async () => {
  const { el: $vuetify } = await import("vuetify/locale");
  const { default: elGR } = await import("../messages/el-GR.json");
  return {
    ...elGR,
    $vuetify,
  };
});
