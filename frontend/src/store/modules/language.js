// This is the data store for the options for language selection. Property is reference only, you cannot set this property.
const state = {
  allLangs: [
    {
      name: "English",
      value: "en-US",
    },
    {
      name: "Dansk (Danish)",
      value: "da-DK",
    },
    {
      name: "Français (French)",
      value: "fr-FR",
    },
    {
      name: "Nederlands (Dutch)",
      value: "nl-NL",
    },
    {
      name: "Polski (Polish)",
      value: "pl-PL",
    },
    {
      name: "Svenska (Swedish)",
      value: "sv-SE",
    },
    {
      name: "简体中文 (Chinese simplified)",
      value: "zh-CN",
    },
    {
      name: "繁體中文 (Chinese traditional)",
      value: "zh-TW",
    },
    {
      name: "Deutsch (German)",
      value: "de-DE",
    },
    {
      name: "Português (Portuguese)",
      value: "pt-PT",
    },
  ],
};

const getters = {
  getAllLangs: state => state.allLangs,
};

export default {
  state,
  getters,
};
