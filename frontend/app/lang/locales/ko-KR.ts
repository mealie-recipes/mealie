export default defineI18nLocale(async () => {
  const { ko: $vuetify } = await import("vuetify/locale");
  const { default: koKR } = await import("../messages/ko-KR.json");
  return {
    ...koKR,
    $vuetify,
  };
});
