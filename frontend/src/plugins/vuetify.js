import Vue from "vue";
import Vuetify from "vuetify/lib";

Vue.use(Vuetify);

import de from "vuetify/es5/locale/de";
import en from "vuetify/es5/locale/en";
import es from "vuetify/es5/locale/es";
import fr from "vuetify/es5/locale/fr";
import hu from "vuetify/es5/locale/hu";
import it from "vuetify/es5/locale/it";
import nl from "vuetify/es5/locale/nl";
import pl from "vuetify/es5/locale/pl";
import sv from "vuetify/es5/locale/sv";
import zhHans from "vuetify/es5/locale/zh-Hans";

const vuetify = new Vuetify({
  theme: {
    dark: false,
    options: { customProperties: true },

    themes: {
      light: {
        primary: "#E58325",
        accent: "#00457A",
        secondary: "#973542",
        success: "#43A047",
        info: "#FFFD99",
        warning: "#FF4081",
        error: "#EF5350",
      },
      dark: {
        primary: "#4527A0",
        accent: "#FF4081",
        secondary: "#26C6DA",
        success: "#43A047",
        info: "#2196F3",
        warning: "#FB8C00",
        error: "#FF5252",
      },
    },
  },
  lang: {
    locales: {
      "de-DE": de,
      "en-US": en,
      "en-GB": en,
      "es-ES": es,
      "fr-FR": fr,
      "hu-HU": hu,
      "it-IT": it,
      "nl-NL": nl,
      "pl-PL": pl,
      "sv-SE": sv,
      "zh-CN": zhHans,
    },
    current: "en-US",
  },
  icons: {
    iconfont: "mdiSvg",
  },
});

export default vuetify;
export { vuetify };
