import Vue from "vue";
import VueI18n from "vue-i18n";
import Vuetify from "@/plugins/vuetify";
import axios from 'axios';

Vue.use(VueI18n);

function parseLocaleFiles(locales) {
  const messages = {};
  locales.keys().forEach(key => {
    const matched = key.match(/([A-Za-z0-9-_]+)\./i);
    if (matched && matched.length > 1) {
      const locale = matched[1];
      messages[locale] = locales(key);
    }
  });
  return messages;
}

function loadDateTimeFormats() {
  const locales = require.context("./locales/dateTimeFormats", true, /[A-Za-z0-9-_,\s]+\.json$/i);
  return parseLocaleFiles(locales);
}

const i18n = new VueI18n({
  dateTimeFormats: loadDateTimeFormats(),
});

export default i18n;

const loadedLanguages = [];

function setI18nLanguage (lang) {
  i18n.locale = lang;
  Vuetify.framework.lang.current = lang;
  axios.defaults.headers.common['Accept-Language'] = lang
  document.querySelector('html').setAttribute('lang', lang)
  return lang
}

export function loadLanguageAsync(lang) {
    // If the same language
  if (i18n.locale === lang) {
    return Promise.resolve(setI18nLanguage(lang))
  }

  // If the language was already loaded
  if (loadedLanguages.includes(lang)) {
    return Promise.resolve(setI18nLanguage(lang))
  }
  
   return import(`./locales/messages/${lang}.json`).then(
    messages => {
      i18n.setLocaleMessage(lang, messages.default)
      loadedLanguages.push(lang)
      return setI18nLanguage(lang)
    }
  ) 
}