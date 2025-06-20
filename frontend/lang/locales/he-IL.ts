export default defineI18nLocale(async () => {
  const { he: $vuetify } = await import("vuetify/locale");
  const { default: heIL } = await import("../messages/he-IL.json");
  return {
    ...heIL,
    $vuetify,
  };
});
