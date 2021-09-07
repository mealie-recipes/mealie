export default {
  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    titleTemplate: "%s - Mealie",
    title: "Home",
    meta: [
      { charset: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { hid: "description", name: "description", content: "" },
      { name: "format-detection", content: "telephone=no" },
    ],
    link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
  },

  env: {
    GLOBAL_MIDDLEWARE: process.env.GLOBAL_MIDDLEWARE || null,
    ALLOW_SIGNUP: process.env.ALLOW_SIGNUP || true,
  },

  router: {
    base: process.env.SUB_PATH || "",
  },

  layoutTransition: {
    name: "layout",
    mode: "out-in",
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [{ src: "~/assets/main.css" }, { src: "~/assets/style-overrides.scss" }],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: ["~/plugins/globals.ts"],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    // https://go.nuxtjs.dev/typescript
    "@nuxt/typescript-build",
    // https://go.nuxtjs.dev/vuetify
    // https://go.nuxtjs.dev/vuetify
    "@nuxtjs/vuetify",
    // https://composition-api.nuxtjs.org/getting-started/setup
    "@nuxtjs/composition-api/module",
    // https://vite.nuxtjs.org/getting-started/installation
    "nuxt-vite",
    // https://github.com/antfu/vue2-script-setup-transform
    "vue2-script-setup-transform/nuxt",
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    // https://go.nuxtjs.dev/axios
    "@nuxtjs/axios",
    // https://go.nuxtjs.dev/pwa
    "@nuxtjs/pwa",
    // https://i18n.nuxtjs.org/setup
    "@nuxtjs/i18n",
    // https://auth.nuxtjs.org/guide/setup
    "@nuxtjs/auth-next",
    // https://github.com/nuxt-community/proxy-module
    [
      "@nuxtjs/proxy",
      {
        logProvider: () => {
          const provider = {
            log: console.log,
            debug: console.log,
            info: console.info,
            warn: console.warn,
            error: console.error,
          };

          return provider;
        },
        logLevel: "debug",
      },
    ],
  ],

  auth: {
    redirect: {
      login: "/login",
      logout: "/login",
      callback: "/login",
      home: "/",
    },
    // Options
    strategies: {
      local: {
        resetOnError: true,
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
            url: "api/auth/token",
            method: "post",
            propertyName: "access_token",
          },
          refresh: { url: "api/auth/refresh", method: "post" },
          user: { url: "api/users/self", method: "get" },
        },
      },
    },
  },

  i18n: {
    locales: [
      // CODE_GEN_ID: MESSAGE_LOCALES
      { code: "el-GR", file: "el-GR.json" },
      { code: "it-IT", file: "it-IT.json" },
      { code: "ko-KR", file: "ko-KR.json" },
      { code: "es-ES", file: "es-ES.json" },
      { code: "ja-JP", file: "ja-JP.json" },
      { code: "zh-CN", file: "zh-CN.json" },
      { code: "tr-TR", file: "tr-TR.json" },
      { code: "ar-SA", file: "ar-SA.json" },
      { code: "hu-HU", file: "hu-HU.json" },
      { code: "pt-PT", file: "pt-PT.json" },
      { code: "no-NO", file: "no-NO.json" },
      { code: "sv-SE", file: "sv-SE.json" },
      { code: "ro-RO", file: "ro-RO.json" },
      { code: "uk-UA", file: "uk-UA.json" },
      { code: "pl-PL", file: "pl-PL.json" },
      { code: "da-DK", file: "da-DK.json" },
      { code: "pt-BR", file: "pt-BR.json" },
      { code: "de-DE", file: "de-DE.json" },
      { code: "ca-ES", file: "ca-ES.json" },
      { code: "sr-SP", file: "sr-SP.json" },
      { code: "cs-CZ", file: "cs-CZ.json" },
      { code: "fr-FR", file: "fr-FR.json" },
      { code: "zh-TW", file: "zh-TW.json" },
      { code: "af-ZA", file: "af-ZA.json" },
      { code: "ru-RU", file: "ru-RU.json" },
      { code: "he-IL", file: "he-IL.json" },
      { code: "nl-NL", file: "nl-NL.json" },
      { code: "en-US", file: "en-US.json" },
      { code: "en-GB", file: "en-GB.json" },
      { code: "fi-FI", file: "fi-FI.json" },
      { code: "vi-VN", file: "vi-VN.json" },
      // END: MESSAGE_LOCALES
    ],
    lazy: true,
    langDir: "lang/messages",
    defaultLocale: "en-US",
    vueI18n: {
      dateTimeFormats: {
        // CODE_GEN_ID: DATE_LOCALES
        "el-GR": require("./lang/dateTimeFormats/el-GR.json"),
        "it-IT": require("./lang/dateTimeFormats/it-IT.json"),
        "ko-KR": require("./lang/dateTimeFormats/ko-KR.json"),
        "es-ES": require("./lang/dateTimeFormats/es-ES.json"),
        "ja-JP": require("./lang/dateTimeFormats/ja-JP.json"),
        "zh-CN": require("./lang/dateTimeFormats/zh-CN.json"),
        "tr-TR": require("./lang/dateTimeFormats/tr-TR.json"),
        "ar-SA": require("./lang/dateTimeFormats/ar-SA.json"),
        "hu-HU": require("./lang/dateTimeFormats/hu-HU.json"),
        "pt-PT": require("./lang/dateTimeFormats/pt-PT.json"),
        "no-NO": require("./lang/dateTimeFormats/no-NO.json"),
        "sv-SE": require("./lang/dateTimeFormats/sv-SE.json"),
        "ro-RO": require("./lang/dateTimeFormats/ro-RO.json"),
        "uk-UA": require("./lang/dateTimeFormats/uk-UA.json"),
        "pl-PL": require("./lang/dateTimeFormats/pl-PL.json"),
        "da-DK": require("./lang/dateTimeFormats/da-DK.json"),
        "pt-BR": require("./lang/dateTimeFormats/pt-BR.json"),
        "de-DE": require("./lang/dateTimeFormats/de-DE.json"),
        "ca-ES": require("./lang/dateTimeFormats/ca-ES.json"),
        "sr-SP": require("./lang/dateTimeFormats/sr-SP.json"),
        "cs-CZ": require("./lang/dateTimeFormats/cs-CZ.json"),
        "fr-FR": require("./lang/dateTimeFormats/fr-FR.json"),
        "zh-TW": require("./lang/dateTimeFormats/zh-TW.json"),
        "af-ZA": require("./lang/dateTimeFormats/af-ZA.json"),
        "ru-RU": require("./lang/dateTimeFormats/ru-RU.json"),
        "he-IL": require("./lang/dateTimeFormats/he-IL.json"),
        "nl-NL": require("./lang/dateTimeFormats/nl-NL.json"),
        "en-US": require("./lang/dateTimeFormats/en-US.json"),
        "en-GB": require("./lang/dateTimeFormats/en-GB.json"),
        "fi-FI": require("./lang/dateTimeFormats/fi-FI.json"),
        "vi-VN": require("./lang/dateTimeFormats/vi-VN.json"),
        // END: DATE_LOCALES
      },
    },
    fallbackLocale: "es",
  },

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  axios: {
    proxy: true,
  },

  publicRuntimeConfig: {
    GLOBAL_MIDDLEWARE: process.env.GLOBAL_MIDDLEWARE || null,
    ALLOW_SIGNUP: process.env.ALLOW_SIGNUP || true,
    SUB_PATH: process.env.SUB_PATH || "",
    axios: {
      browserBaseURL: process.env.SUB_PATH || "",
    },
  },

  privateRuntimeConfig: {},

  proxy: {
    // "http://localhost:9000/*/api",
    // See Proxy section
    [`${process.env.SUB_PATH || ""}api`]: {
      pathRewrite: {
        [`${process.env.SUB_PATH || ""}api`]: "/api", // rewrite path
      },
      changeOrigin: true,
      target: process.env.API_URL || "http://localhost:9000",
    },
    "/api": {
      changeOrigin: true,
      target: process.env.API_URL || "http://localhost:9000",
    },
  },

  // PWA module configuration: https://go.nuxtjs.dev/pwa
  pwa: {
    manifest: {
      lang: "en",
    },
  },

  // Vuetify module configuration: https://go.nuxtjs.dev/config-vuetify
  vuetify: {
    customVariables: ["~/assets/variables.scss"],
    icons: {
      iconfont: "mdiSvg", // 'mdi' || 'mdiSvg' || 'md' || 'fa' || 'fa4' || 'faSvg'
    },
    defaultAssets: {
      font: {
        family: "Roboto",
      },
      icons: false,
    },
    theme: {
      options: {
        customProperties: true,
      },
      dark: false,
      themes: {
        dark: {
          primary: "#E58325",
          accent: "#007A99",
          secondary: "#973542",
          success: "#43A047",
          info: "#1976d2",
          warning: "#FF6D00",
          error: "#EF5350",
        },
        light: {
          primary: "#E58325",
          accent: "#007A99",
          secondary: "#973542",
          success: "#43A047",
          info: "#1976d2",
          warning: "#FF6D00",
          error: "#EF5350",
        },
      },
    },
  },

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {
    // https://nuxtjs.org/docs/2.x/configuration-glossary/configuration-build
    analyze: process.env.NODE_ENV !== "production",
    babel: {
      plugins: [["@babel/plugin-proposal-private-property-in-object", { loose: true }]],
    },
    transpile: process.env.NODE_ENV !== "production" ? [/@vue[\\/]composition-api/] : null,
  },
};
