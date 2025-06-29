export default defineI18nLocale(async () => {
  const { ja: $vuetify } = await import("vuetify/locale");
  const { default: jaJP } = await import("../messages/ja-JP.json");
  return {
    ...jaJP,
    $vuetify,
  };
});
