export default defineI18nLocale(async () => {
  const { pt: $vuetify } = await import("vuetify/locale");
  const { default: ptBR } = await import("../messages/pt-BR.json");
  return {
    ...ptBR,
    $vuetify,
  };
});
