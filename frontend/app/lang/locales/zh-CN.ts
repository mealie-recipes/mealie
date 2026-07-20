export default defineI18nLocale(async () => {
  const { zhHans: $vuetify } = await import("vuetify/locale");
  const { default: zhCN } = await import("../messages/zh-CN.json");
  return {
    ...zhCN,
    $vuetify,
  };
});
