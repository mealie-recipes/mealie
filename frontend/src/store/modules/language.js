// This is the data store for the options for language selection. Property is reference only, you cannot set this property.
const state = {
  allLangs: [
    {
      name: "American English",
      value: "en-US",
    },
    {
      name: "British English",
      value: "en-GB",
    },
    {
      name: "Català (Catalan)",
      value: "ca-ES",
    },
    {
      name: "Dansk (Danish)",
      value: "da-DK",
    },
    {
      name: "Deutsch (German)",
      value: "de-DE",
    },
    {
      name: "Español (Spanish)",
      value: "es-ES",
    },
    {
      name: "Français (French)",
      value: "fr-FR",
    },
    {
      name: "Français Canadien (Canadian French)",
      value: "fr-CA",
    },
    {
      name: "Magyar (Hungarian)",
      value: "hu-HU",
    },
    {
      name: "Italiano (Italian)",
      value: "it-IT",
    },
    {
      name: "Norsk (Norwegian)",
      value: "no-NO",
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
      name: "Pусский (Russian)",
      value: "ru-RU",
    },
    {
      name: "Українська (Ukrainian)",
      value: "uk-UA",
    },
    {
      name: "Slovenčina (Slovak)",
      value: "sk-SK",
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
  ],
};

const getters = {
  getAllLangs: state => state.allLangs,
};

export default {
  state,
  getters,
};
