export default defineI18nLocale(async () => {
  const { vi: $vuetify } = await import("vuetify/locale");
  const { default: viVN } = await import("../messages/vi-VN.json");
  return {
    ...viVN,
    $vuetify,
  };
});
