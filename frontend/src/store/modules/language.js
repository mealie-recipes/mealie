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
      name: "Italiano (Italian)",
      value: "it-IT",
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
  ],
};

const getters = {
  getAllLangs: state => state.allLangs,
};

export default {
  state,
  getters,
};
