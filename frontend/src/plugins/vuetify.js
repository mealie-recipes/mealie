import Vue from "vue";
import Vuetify from "vuetify/lib";

Vue.use(Vuetify);

const vuetify = new Vuetify({
  theme: {
    dark: false,
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
});

export default vuetify;
export { vuetify };
