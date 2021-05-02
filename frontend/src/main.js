import Vue from "vue";
import App from "./App.vue";
import vuetify from "./plugins/vuetify";
import store from "./store";
import VueRouter from "vue-router";
import { router } from "./routes";
import i18n from "./i18n";
import FlashMessage from "@smartweb/vue-flash-message";
import "@mdi/font/css/materialdesignicons.css";
import "typeface-roboto/index.css";

Vue.use(FlashMessage);
Vue.config.productionTip = false;
Vue.use(VueRouter);

const vueApp = new Vue({
  vuetify,
  store,
  router,
  i18n,
  render: h => h(App),
}).$mount("#app");

// Truncate
const truncate = function(text, length, clamp) {
  clamp = clamp || "...";
  let node = document.createElement("div");
  node.innerHTML = text;
  let content = node.textContent;
  return content.length > length ? content.slice(0, length) + clamp : content;
};

const titleCase = function(value) {
  return value.replace(/(?:^|\s|-)\S/g, x => x.toUpperCase());
};

Vue.filter("truncate", truncate);
Vue.filter("titleCase", titleCase);

export { router, vueApp };
