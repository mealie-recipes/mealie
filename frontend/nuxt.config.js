export default {
  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    titleTemplate: "%s - frontend",
    title: "frontend",
    meta: [
      { charset: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { hid: "description", name: "description", content: "" },
      { name: "format-detection", content: "telephone=no" },
    ],
    link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
  },

  layoutTransition: {
    name: "layout",
    mode: "out-in",
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [{ src: "~/assets/main.css" }, { src: "~/assets/style-overrides.scss" }],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: ["~/plugins/globals.js"],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    // https://go.nuxtjs.dev/typescript
    "@nuxt/typescript-build",
    // https://go.nuxtjs.dev/vuetify
    "@nuxtjs/vuetify",
    // https://composition-api.nuxtjs.org/getting-started/setup
    "@nuxtjs/composition-api/module",
  ],

  env: {
    PUBLIC_SITE: process.env.PUBLIC_SITE || true,
    BASE_URL: process.env.BASE_URL || "",
    ALLOW_SIGNUP: process.env.ALLOW_SIGNUP || true,
  },

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    // https://go.nuxtjs.dev/axios
    "@nuxtjs/axios",
    // https://go.nuxtjs.dev/pwa
    "@nuxtjs/pwa",
    // https://i18n.nuxtjs.org/setup
    "nuxt-i18n",
    // https://auth.nuxtjs.org/guide/setup
    "@nuxtjs/auth-next",
    // https://github.com/nuxt-community/proxy-module
    "@nuxtjs/proxy",
  ],

  proxy: {
    // see Proxy section
    "/api": {
      changeOrigin: true,
      target: "http://localhost:9000",
    },
  },

  auth: {
    redirect: {
      login: "/user/login",
      logout: "/",
      callback: "/login",
      home: "/",
    },
    // Options
    strategies: {
      local: {
        token: {
          property: "access_token",
          global: true,
          // required: true,
          // type: 'Bearer'
        },
        user: {
          property: "",
          autoFetch: true,
        },
        endpoints: {
          login: {
            url: "/api/auth/token",
            method: "post",
            propertyName: "access_token",
          },
          refresh: { url: "/api/auth/refresh", method: "post" },
          user: { url: "/api/users/self", method: "get" },
        },
      },
    },
  },

  i18n: {
    locales: [
      {
        code: "en-US",
        file: "en-US.js",
      },
    ],
    lazy: true,
    langDir: "lang/messages",
    defaultLocale: "en-US",
  },

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  axios: {},

  // PWA module configuration: https://go.nuxtjs.dev/pwa
  pwa: {
    manifest: {
      lang: "en",
    },
  },

  // Vuetify module configuration: https://go.nuxtjs.dev/config-vuetify
  vuetify: {
    customVariables: ["~/assets/variables.scss"],
    theme: {
      dark: false,
      themes: {
        dark: {
          primary: "#E58325",
          accent: "#00457A",
          secondary: "#973542",
          success: "#43A047",
          info: "#4990BA",
          warning: "#FF4081",
          error: "#EF5350",
        },
        light: {
          primary: "#E58325",
          accent: "#00457A",
          secondary: "#973542",
          success: "#43A047",
          info: "#4990BA",
          warning: "#FF4081",
          error: "#EF5350",
        },
      },
    },
  },

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {},
};
