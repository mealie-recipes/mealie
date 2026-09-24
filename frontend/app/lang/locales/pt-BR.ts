export default defineI18nLocale(async () => {
  const { pt: $vuetify } = await import("vuetify/locale");
  const { default: ptBR } = await import("../messages/pt-BR.json");
  const { default: unitNames } = await import(
    "../../../../mealie/repos/seed/resources/units/locales/pt-BR.json",
  );
  return {
    ...ptBR,
    "unit-names": unitNames,
    $vuetify,
  };
});
