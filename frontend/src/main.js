import Vue from "vue";
import App from "./App.vue";
import vuetify from "./plugins/vuetify";
import store from "./store/store";
import VueRouter from "vue-router";
import { routes } from "./routes";

Vue.config.productionTip = false;
Vue.use(VueRouter);

const router = new VueRouter({
  routes,
  mode: process.env.NODE_ENV === "production" ? "history" : "hash",
});

new Vue({
  vuetify,
  store,
  router,
  render: (h) => h(App),
}).$mount("#app");

// Truncate
let filter = function(text, length, clamp) {
  clamp = clamp || "...";
  let node = document.createElement("div");
  node.innerHTML = text;
  let content = node.textContent;
  return content.length > length ? content.slice(0, length) + clamp : content;
};

Vue.filter("truncate", filter);

export { router };
