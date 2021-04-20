import Vue from "vue";
import Vuetify from "vuetify/lib";

Vue.use(Vuetify);

// language IDs should match those from VueI18n with _ instead of - 
import de_DE from 'vuetify/es5/locale/de';
import en_US from 'vuetify/es5/locale/en';
import fr_FR from 'vuetify/es5/locale/fr';
import pl_PL from 'vuetify/es5/locale/pl';
import pt_PT from 'vuetify/es5/locale/pt';
import sv_SE from 'vuetify/es5/locale/sv';
import zh_CN from 'vuetify/es5/locale/zh-Hans';
import zh_TW from 'vuetify/es5/locale/zh-Hant';


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
      de_DE,
      en_US, 
      fr_FR, 
      pl_PL, 
      pt_PT, 
      sv_SE, 
      zh_CN,
      zh_TW
    },
    current: 'en_US',
  },
});

export default vuetify;
export { vuetify };
