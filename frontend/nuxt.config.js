export default {
  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    title: "Mealie",
    meta: [
      { hid: "og:type", property: "og:type", content: "website" },
      { hid: "og:title", property: "og:title", content: "Mealie" },
      { hid: "og:site_name", property: "og:site_name", content: "Mealie" },
      {
        hid: "og:description",
        property: "og:description",
        content: "Mealie is a recipe management app for your kitchen.",
      },
      {
        hid: "og:image",
        property: "og:image",
        content:
          "https://raw.githubusercontent.com/hay-kot/mealie/dev/frontend/public/img/icons/android-chrome-512x512.png",
      },
      { charset: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      {
        hid: "description",
        name: "description",
        content: "Mealie is a recipe management app for your kitchen.",
      },
    ],
    link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
  },

  env: {
    GLOBAL_MIDDLEWARE: process.env.GLOBAL_MIDDLEWARE || null,
  },

  router: {
    base: process.env.SUB_PATH || "",
  },

  layoutTransition: {
    name: "layout",
    mode: "out-in",
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [{ src: "~/assets/css/main.css" }, { src: "~/assets/css/main.css" }, { src: "~/assets/style-overrides.scss" }],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: ["~/plugins/globals.ts", "~/plugins/theme.ts", "~/plugins/toast.client.ts", "~/plugins/dark-mode.client.ts"],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    // https://go.nuxtjs.dev/typescript
    [
      "@nuxt/typescript-build",
      // Fix slow builds
      // https://github.com/nuxt/nuxt.js/issues/8310#issuecomment-734984360
      {
        typeCheck: {
          typescript: {
            enabled: true,
            mode: "write-tsbuildinfo",
          },
        },
      },
    ],
    // https://go.nuxtjs.dev/vuetify
    "@nuxtjs/vuetify",
    // https://composition-api.nuxtjs.org/getting-started/setup
    "@nuxtjs/composition-api/module",
    // https://vite.nuxtjs.org/getting-started/installation
    "nuxt-vite",
    // https://google-fonts.nuxtjs.org/setup
    "@nuxtjs/google-fonts",
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

  googleFonts: {
    fontsPath: "/assets/fonts",
    download: true,
    families: {
      Roboto: [100, 300, 400, 500, 700, 900],
    },
  },

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
      { code: "bg-BG", file: "bg-BG.json" },
      { code: "zh-CN", file: "zh-CN.json" },
      { code: "tr-TR", file: "tr-TR.json" },
      { code: "ar-SA", file: "ar-SA.json" },
      { code: "hu-HU", file: "hu-HU.json" },
      { code: "pt-PT", file: "pt-PT.json" },
      { code: "no-NO", file: "no-NO.json" },
      { code: "sv-SE", file: "sv-SE.json" },
      { code: "ro-RO", file: "ro-RO.json" },
      { code: "sk-SK", file: "sk-SK.json" },
      { code: "uk-UA", file: "uk-UA.json" },
      { code: "lt-LT", file: "lt-LT.json" },
      { code: "fr-CA", file: "fr-CA.json" },
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
      { code: "sl-SI", file: "sl-SI.json" },
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
    strategy: "no_prefix",
    langDir: "lang/messages",
    detectBrowserLanguage: {
      useCookie: true,
      alwaysRedirect: true,
    },
    defaultLocale: "en-US",
    vueI18n: {
      dateTimeFormats: {
        // CODE_GEN_ID: DATE_LOCALES
        "el-GR": require("./lang/dateTimeFormats/el-GR.json"),
        "it-IT": require("./lang/dateTimeFormats/it-IT.json"),
        "ko-KR": require("./lang/dateTimeFormats/ko-KR.json"),
        "es-ES": require("./lang/dateTimeFormats/es-ES.json"),
        "ja-JP": require("./lang/dateTimeFormats/ja-JP.json"),
        "bg-BG": require("./lang/dateTimeFormats/bg-BG.json"),
        "zh-CN": require("./lang/dateTimeFormats/zh-CN.json"),
        "tr-TR": require("./lang/dateTimeFormats/tr-TR.json"),
        "ar-SA": require("./lang/dateTimeFormats/ar-SA.json"),
        "hu-HU": require("./lang/dateTimeFormats/hu-HU.json"),
        "pt-PT": require("./lang/dateTimeFormats/pt-PT.json"),
        "no-NO": require("./lang/dateTimeFormats/no-NO.json"),
        "sv-SE": require("./lang/dateTimeFormats/sv-SE.json"),
        "ro-RO": require("./lang/dateTimeFormats/ro-RO.json"),
        "sk-SK": require("./lang/dateTimeFormats/sk-SK.json"),
        "uk-UA": require("./lang/dateTimeFormats/uk-UA.json"),
        "fr-CA": require("./lang/dateTimeFormats/fr-CA.json"),
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
      fallbackLocale: "en-US",
    },
  },

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  axios: {
    proxy: true,
  },

  publicRuntimeConfig: {
    GLOBAL_MIDDLEWARE: process.env.GLOBAL_MIDDLEWARE || null,
    SUB_PATH: process.env.SUB_PATH || "",
    axios: {
      browserBaseURL: process.env.SUB_PATH || "",
    },
    // ==============================================
    // Theme Runtime Config
    useDark: process.env.THEME_USE_DARK || false,
    themes: {
      dark: {
        primary: process.env.THEME_DARK_PRIMARY || "#E58325",
        accent: process.env.THEME_DARK_ACCENT || "#007A99",
        secondary: process.env.THEME_DARK_SECONDARY || "#973542",
        success: process.env.THEME_DARK_SUCCESS || "#43A047",
        info: process.env.THEME_DARK_INFO || "#1976d2",
        warning: process.env.THEME_DARK_WARNING || "#FF6D00",
        error: process.env.THEME_DARK_ERROR || "#EF5350",
        background: "#202021",
      },
      light: {
        primary: process.env.THEME_LIGHT_PRIMARY || "#E58325",
        accent: process.env.THEME_LIGHT_ACCENT || "#007A99",
        secondary: process.env.THEME_DARK_SECONDARY || "#973542",
        success: process.env.THEME_DARK_SUCCESS || "#43A047",
        info: process.env.THEME_LIGHT_INFO || "#1976d2",
        warning: process.env.THEME_LIGHT_WARNING || "#FF6D00",
        error: process.env.THEME_LIGHT_ERROR || "#EF5350",
      },
    },
  },

  privateRuntimeConfig: {},

  proxy: {
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
    meta: {
      /* meta options */
      name: "Mealie",
      description: "Mealie is a recipe management and meal planning app",
      theme_color: "#E58325",
      ogSiteName: "Mealie",
    },
    manifest: {
      lang: "en",
      name: "Mealie",
      title: "Mealie",
      background_color: "#FFFFFF",
      share_target: {
        action: "/",
        method: "GET",
        params: {
          title: "title",
          text: "recipe_import_url",
        },
      },
      workbox: {
        /* workbox options */
        skipWaiting: "true",
      },
    },
    icons: [
      {
        src: "[srcDir]/[staticDir]/icons/android-chrome-192x192.png",
        sizes: "192x192",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "[srcDir]/[staticDir]/icons/android-chrome-512x512.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "[srcDir]/[staticDir]/icons/android-chrome-maskable-192x192.png",
        sizes: "192x192",
        type: "image/png",
        purpose: "maskable",
      },
      {
        src: "[srcDir]/[staticDir]/icons/android-chrome-maskable-512x512.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "maskable",
      },
    ],
  },

  // Vuetify module configuration: https://go.nuxtjs.dev/config-vuetify
  vuetify: {
    customVariables: ["~/assets/variables.scss"],
    icons: {
      iconfont: "mdiSvg", // 'mdi' || 'mdiSvg' || 'md' || 'fa' || 'fa4' || 'faSvg'
    },
    defaultAssets: false,
    theme: {
      options: {
        customProperties: true,
      },
      dark: false,
      // Theme Config set at runtime by /plugins/theme.ts
      // This config doesn't do anything.
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
    analyze: false,
    babel: {
      plugins: [
        ["@babel/plugin-proposal-private-property-in-object", { loose: true }],
        // ["@nuxtjs/composition-api/dist/babel-plugin"],
      ],
    },
    transpile: process.env.NODE_ENV !== "production" ? [/@vue[\\/]composition-api/] : null,
  },
};
