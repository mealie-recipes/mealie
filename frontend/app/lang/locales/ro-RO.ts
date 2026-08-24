export default defineI18nLocale(async () => {
  const { ro: $vuetify } = await import("vuetify/locale");
  const { default: roRO } = await import("../messages/ro-RO.json");
  return {
    ...roRO,
    $vuetify,
  };
});
