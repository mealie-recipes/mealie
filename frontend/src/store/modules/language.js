// This is the data store for the options for language selection. Property is reference only, you cannot set this property.
const state = {
  allLangs: [
    {
      name: "English",
      value: "en-US",
    },
    {
      name: "Danish",
      value: "da-DK",
    },
    {
      name: "French",
      value: "fr-FR",
    },
    {
      name: "Polish",
      value: "pl-PL",
    },
    {
      name: "Swedish",
      value: "sv-SE",
    },
    {
      name: "简体中文",
      value: "zh-CN",
    },
    {
      name: "繁體中文",
      value: "zh-TW",
    },
    {
      name: "German",
      value: "de-DE",
    },
    {
      name: "Português",
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
