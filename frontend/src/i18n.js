import Vue from "vue";
import VueI18n from "vue-i18n";

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

function loadLocaleMessages() {
  const locales = require.context(
    "./locales/messages",
    true,
    /[A-Za-z0-9-_,\s]+\.json$/i
  );
  return parseLocaleFiles(locales);
}

function loadDateTimeFormats() {
  const locales = require.context(
    "./locales/dateTimeFormats",
    true,
    /[A-Za-z0-9-_,\s]+\.json$/i
  );
  return parseLocaleFiles(locales);
}


export default new VueI18n({
  locale: "en",
  fallbackLocale: process.env.VUE_APP_I18N_FALLBACK_LOCALE || "en",
  messages: loadLocaleMessages(),
  dateTimeFormats: loadDateTimeFormats() 
});
