export default defineI18nLocale(async () => {
  const { zhHant: $vuetify } = await import("vuetify/locale");
  const { default: zhTW } = await import("../messages/zh-TW.json");
  return {
    ...zhTW,
    $vuetify,
  };
});
