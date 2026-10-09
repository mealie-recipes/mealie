export default defineI18nLocale(async () => {
  const { ko: $vuetify } = await import("vuetify/locale");
  const { default: koKR } = await import("../messages/ko-KR.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/ko-KR.json",
  );
  return {
    ...koKR,
    "unit-names": unitNames,
    $vuetify,
  };
});
