import Vue from "vue";
import VueI18n from "vue-i18n";
import Vuetify from "@/plugins/vuetify";
import axios from 'axios';

Vue.use(VueI18n);

const i18n = new VueI18n();

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

  const messages = import(`./locales/messages/${lang}.json`);
  const dateTimeFormats = import(`./locales/dateTimeFormats/${lang}.json`);
  
  return Promise.all([messages, dateTimeFormats]).then(
    values  => {
      i18n.setLocaleMessage(lang, values[0].default)
      i18n.setDateTimeFormat(lang, values[1].default)
      loadedLanguages.push(lang)
      return setI18nLanguage(lang)
    }
  ) 
}