export default {
  // Global page headers: https://go.nuxtjs.dev/config-head
  target: "static",
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
          "https://raw.githubusercontent.com/mealie-recipes/mealie/9571816ac4eed5beacfc0abf6c03eff1427fd0eb/frontend/static/icons/android-chrome-512x512.png",
      },
      { charset: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      {
        hid: "description",
        name: "description",
        content: "Mealie is a recipe management app for your kitchen.",
      },
    ],
    link: [
      { hid: "favicon", rel: "icon", type: "image/x-icon", href: "/favicon.ico", "data-n-head": "ssr" },
      { hid: "shortcut icon", rel: "shortcut icon", type: "image/png", href: "/icons/icon-x64.png", "data-n-head": "ssr" },
      { hid: "apple-touch-icon", rel: "apple-touch-icon", type: "image/png", href: "/icons/apple-touch-icon.png", "data-n-head": "ssr" },
      { hid: "mask-icon", rel: "mask-icon", href: "/icons/safari-pinned-tab.svg", "data-n-head": "ssr" }
    ],
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
    ...(process.env.NODE_ENV === "production" ? ["@nuxtjs/pwa"] : []),
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
    cookie: {
      prefix: "mealie.auth.",
      options: {
        expires: 7,
        path: "/",
      },
    },
    rewriteRedirects: false,
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
          logout: { url: "api/auth/logout", method: "post" },
          user: { url: "api/users/self", method: "get" },
        },
      },
      oidc: {
        scheme: "local",
        resetOnError: true,
        token: {
          property: "access_token",
          global: true,
        },
        user: {
          property: "",
          autoFetch: true,
        },
        endpoints: {
          login: {
            url: "api/auth/oauth/callback",
            method: "get",
          },
          logout: { url: "api/auth/logout", method: "post" },
          user: { url: "api/users/self", method: "get" },
        },
      },
    },
  },

  i18n: {
    locales: [
      // CODE_GEN_ID: MESSAGE_LOCALES
      { code: "lv-LV", file: "lv-LV.json" },
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
      { code: "hr-HR", file: "hr-HR.json" },
      { code: "da-DK", file: "da-DK.json" },
      { code: "pt-BR", file: "pt-BR.json" },
      { code: "de-DE", file: "de-DE.json" },
      { code: "ca-ES", file: "ca-ES.json" },
      { code: "sr-SP", file: "sr-SP.json" },
      { code: "cs-CZ", file: "cs-CZ.json" },
      { code: "gl-ES", file: "gl-ES.json" },
      { code: "fr-FR", file: "fr-FR.json" },
      { code: "fr-BE", file: "fr-BE.json" },
      { code: "zh-TW", file: "zh-TW.json" },
      { code: "af-ZA", file: "af-ZA.json" },
      { code: "is-IS", file: "is-IS.json" },
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
        "fr-BE": require("./lang/dateTimeFormats/fr-BE.json"),
        "zh-TW": require("./lang/dateTimeFormats/zh-TW.json"),
        "af-ZA": require("./lang/dateTimeFormats/af-ZA.json"),
        "ru-RU": require("./lang/dateTimeFormats/ru-RU.json"),
        "he-IL": require("./lang/dateTimeFormats/he-IL.json"),
        "nl-NL": require("./lang/dateTimeFormats/nl-NL.json"),
        "en-US": require("./lang/dateTimeFormats/en-US.json"),
        "en-GB": require("./lang/dateTimeFormats/en-GB.json"),
        "fi-FI": require("./lang/dateTimeFormats/fi-FI.json"),
        "vi-VN": require("./lang/dateTimeFormats/vi-VN.json"),
        "sl-SI": require("./lang/dateTimeFormats/sl-SI.json"),
        "lv-LV": require("./lang/dateTimeFormats/lv-LV.json"),
        "is-IS": require("./lang/dateTimeFormats/is-IS.json"),
        "gl-ES": require("./lang/dateTimeFormats/gl-ES.json"),
        "lt-LT": require("./lang/dateTimeFormats/lt-LT.json"),
        "hr-HR": require("./lang/dateTimeFormats/hr-HR.json"),
        // END: DATE_LOCALES
      },
      fallbackLocale: "en-US",
    },
  },

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  axios: {
    proxy: true,
    credentials: true,
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
        background: "#1E1E1E",
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
      xfwd: true,
    },
    "/api": {
      changeOrigin: true,
      target: process.env.API_URL || "http://localhost:9000",
      xfwd: true,
    },
    "/docs": {
      changeOrigin: true,
      target: process.env.API_URL || "http://localhost:9000",
      xfwd: true,
    },
    "/openapi.json": {
      changeOrigin: true,
      target: process.env.API_URL || "http://localhost:9000",
      xfwd: true,
    },
  },

  // PWA module configuration: https://go.nuxtjs.dev/pwa
  pwa: {
    meta: {
      /* meta options */
      name: "Mealie",
      description: "Mealie is a recipe management and meal planning app",
      theme_color: process.env.THEME_LIGHT_PRIMARY || "#E58325",
      ogSiteName: "Mealie",
    },
    manifest: {
      start_url: "/",
      scope: "/",
      lang: "en",
      dir: "auto",
      name: "Mealie",
      short_name: "Mealie",
      crossorigin: "use-credentials",
      id: "mealie",
      description: "Mealie is a recipe management and meal planning app",
      theme_color: process.env.THEME_LIGHT_PRIMARY || "#E58325",
      background_color: "#FFFFFF",
      display: "standalone",
      display_override: [
        "standalone",
        "minimal-ui",
        "browser",
        "window-controls-overlay"
      ],
      share_target: {
        action: "/r/create/url",
        method: "GET",
        params: {
          /* title and url are not currently used in Mealie. If there are issues
             with sharing, uncommenting those lines might help solve the puzzle. */
          // "title": "title",
          "text": "recipe_import_url",
          // "url": "url",
        },
      },
      icons: [
        {
          src: "/icons/android-chrome-192x192.png",
          sizes: "192x192",
          type: "image/png",
          purpose: "any",
        },
        {
          src: "/icons/android-chrome-512x512.png",
          sizes: "512x512",
          type: "image/png",
          purpose: "any",
        },
        {
          src: "/icons/android-chrome-maskable-192x192.png",
          sizes: "192x192",
          type: "image/png",
          purpose: "maskable",
        },
        {
          src: "/icons/android-chrome-maskable-512x512.png",
          sizes: "512x512",
          type: "image/png",
          purpose: "maskable",
        },
      ],
      screenshots: [
        {
          "src": "/screenshots/home-narrow.png",
          "sizes": "1600x2420",
          "form_factor": "narrow",
          "label": "Home Page"
        },
        {
          "src": "/screenshots/recipe-narrow.png",
          "sizes": "1600x2420",
          "form_factor": "narrow",
          "label": "Recipe Page"
        },
        {
          "src": "/screenshots/editor-narrow.png",
          "sizes": "1600x2420",
          "form_factor": "narrow",
          "label": "Editor Page"
        },
        {
          "src": "/screenshots/parser-narrow.png",
          "sizes": "1600x2420",
          "form_factor": "narrow",
          "label": "Parser Page"
        },
        {
          "src": "/screenshots/home-wide.png",
          "sizes": "2560x1460",
          "form_factor": "wide",
          "label": "Home Page"
        },
        {
          "src": "/screenshots/recipe-wide.png",
          "sizes": "2560x1460",
          "form_factor": "wide",
          "label": "Recipe Page"
        },
        {
          "src": "/screenshots/editor-wide.png",
          "sizes": "2560x1460",
          "form_factor": "wide",
          "label": "Editor Page"
        },
        {
          "src": "/screenshots/parser-wide.png",
          "sizes": "2560x1460",
          "form_factor": "wide",
          "label": "Parser Page"
        }
      ],
      "shortcuts": [
        {
          "name": "Shopping Lists",
          "short_name": "Shopping Lists",
          "description": "Open the shopping lists",
          "url": "/shopping-lists",
          "icons": [
            {
              "src": "/icons/mdiFormatListChecks-192x192.png",
              "sizes": "192x192",
            },
            {
              "src": "/icons/mdiFormatListChecks-96x96.png",
              "sizes": "96x96",
            }
          ]
        },
        {
          "name": "Meal Planner",
          "short_name": "Meal Planner",
          "description": "Open the meal planner",
          "url": "/household/mealplan/planner/view",
          "icons": [
            {
              "src": "/icons/mdiCalendarMultiselect-192x192.png",
              "sizes": "192x192",
            },
            {
              "src": "/icons/mdiCalendarMultiselect-96x96.png",
              "sizes": "96x96",
            }
          ]
        },
      ],
      prefer_related_applications: false,
      handle_links: "preferred",
      categories: [
        "food"
      ],
      launch_handler: {
        "client_mode": ["focus-existing", "auto"]
      },
      edge_side_panel: {
        "preferred_width": 400
      }
    },
    icon: false, // disables the icon module
  },

  // Vuetify module configuration: https://go.nuxtjs.dev/config-vuetify
  vuetify: {
    optionsPath: "./vuetify.options.js",
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
