export default defineI18nLocale(async () => {
  const { cs: $vuetify } = await import("vuetify/locale");
  const { default: csCZ } = await import("../messages/cs-CZ.json");
  return {
    ...csCZ,
    $vuetify,
  };
});
