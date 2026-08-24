export default defineI18nLocale(async () => {
  const { pl: $vuetify } = await import("vuetify/locale");
  const { default: plPL } = await import("../messages/pl-PL.json");
  return {
    ...plPL,
    $vuetify,
  };
});
