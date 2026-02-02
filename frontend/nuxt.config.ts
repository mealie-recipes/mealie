import { defineNuxtConfig } from "nuxt/config";

const AUTH_TOKEN = "mealie.access_token";

export default defineNuxtConfig({
  // Global page headers: https://go.nuxtjs.dev/config-head
  // target: "static",

  modules: [
    "@vite-pwa/nuxt",
    "@nuxtjs/i18n",
    "@nuxt/fonts",
    "vuetify-nuxt-module",
    "@nuxt/eslint",
  ],
  ssr: false,

  components: [
    {
      path: "~/components",
      pathPrefix: false,
    },
  ],
  devtools: {
    enabled: false,
  },

  app: {
    baseURL: process.env.SUB_PATH || "/",

    head: {
      title: "Mealie",
      meta: [
        { property: "og:type", content: "website" },
        { property: "og:title", content: "Mealie" },
        { property: "og:site_name", content: "Mealie" },
        {
          property: "og:description",
          content: "Mealie is a recipe management app for your kitchen.",
        },
        {
          property: "og:image",
          content:
            "https://raw.githubusercontent.com/mealie-recipes/mealie/9571816ac4eed5beacfc0abf6c03eff1427fd0eb/frontend/static/icons/android-chrome-512x512.png",
        },
        { charset: "utf-8" },
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        {
          name: "description",
          content: "Mealie is a recipe management app for your kitchen.",
        },
      ],
      link: [
        { rel: "icon", type: "image/x-icon", href: "/favicon.ico" },
        { rel: "shortcut icon", type: "image/png", href: "/icons/icon-x64.png" },
        { rel: "apple-touch-icon", type: "image/png", href: "/icons/apple-touch-icon.png" },
        { rel: "mask-icon", href: "/icons/safari-pinned-tab.svg" },
        { rel: "manifest", href: "/manifest.webmanifest", crossorigin: "use-credentials" },
      ],
    },

    /* viewTransition: {
      name: "layout",
      mode: "out-in",
    }, */
    viewTransition: true,
  },

  css: ["~/assets/main.css", "~/assets/style-overrides.scss"],

  runtimeConfig: {
    sessionPassword: process.env.SESSION_PASSWORD || "password-with-at-least-32-characters",
    apiUrl: process.env.API_URL || "http://localhost:9000",
    public: {
      AUTH_TOKEN,
      GLOBAL_MIDDLEWARE: process.env.GLOBAL_MIDDLEWARE || undefined,
      SUB_PATH: process.env.SUB_PATH || "",
      // ==============================================
      // Theme Runtime Config
      useDark: Boolean(process.env.THEME_USE_DARK) || false,
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
          secondary: process.env.THEME_LIGHT_SECONDARY || "#973542",
          success: process.env.THEME_LIGHT_SUCCESS || "#43A047",
          info: process.env.THEME_LIGHT_INFO || "#1976d2",
          warning: process.env.THEME_LIGHT_WARNING || "#FF6D00",
          error: process.env.THEME_LIGHT_ERROR || "#EF5350",
        },
      },
    },
  },
  dir: {
    static: "static",
  },

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {
    // https://nuxtjs.org/docs/2.x/configuration-glossary/configuration-build
    analyze: false,
    /* babel: {
      plugins: [
        ["@babel/plugin-proposal-private-property-in-object", { loose: true }],
      ],
    }, */
    transpile: process.env.NODE_ENV !== "production" ? [/@vue[\\/]composition-api/] : [],
  },
  future: {
    compatibilityVersion: 3,
  },

  compatibilityDate: "2025-03-28",

  nitro: {
    baseURL: process.env.SUB_PATH || "",
  },

  // eslint rules
  eslint: {
    config: {
      formatters: true,
      stylistic: {
        indent: 2,
        semi: true,
        quotes: "double",
        commaDangle: "always-multiline",
      },
    },
  },
  fonts: {
    defaults: {
      weights: ["100 900"],
      styles: ["normal", "italic"],
      subsets: ["cyrillic-ext", "cyrillic", "greek-ext", "greek", "vietnamese", "latin-ext", "latin"],
    },
  },

  i18n: {
    locales: [
      // CODE_GEN_ID: MESSAGE_LOCALES
      { code: "af-ZA", file: "af-ZA.ts", dir: "ltr" },
      { code: "ar-SA", file: "ar-SA.ts", dir: "rtl" },
      { code: "bg-BG", file: "bg-BG.ts", dir: "ltr" },
      { code: "ca-ES", file: "ca-ES.ts", dir: "ltr" },
      { code: "cs-CZ", file: "cs-CZ.ts", dir: "ltr" },
      { code: "da-DK", file: "da-DK.ts", dir: "ltr" },
      { code: "de-DE", file: "de-DE.ts", dir: "ltr" },
      { code: "el-GR", file: "el-GR.ts", dir: "ltr" },
      { code: "en-GB", file: "en-GB.ts", dir: "ltr" },
      { code: "en-US", file: "en-US.ts", dir: "ltr" },
      { code: "es-ES", file: "es-ES.ts", dir: "ltr" },
      { code: "et-EE", file: "et-EE.ts", dir: "ltr" },
      { code: "fi-FI", file: "fi-FI.ts", dir: "ltr" },
      { code: "fr-BE", file: "fr-BE.ts", dir: "ltr" },
      { code: "fr-CA", file: "fr-CA.ts", dir: "ltr" },
      { code: "fr-FR", file: "fr-FR.ts", dir: "ltr" },
      { code: "gl-ES", file: "gl-ES.ts", dir: "ltr" },
      { code: "he-IL", file: "he-IL.ts", dir: "rtl" },
      { code: "hr-HR", file: "hr-HR.ts", dir: "ltr" },
      { code: "hu-HU", file: "hu-HU.ts", dir: "ltr" },
      { code: "is-IS", file: "is-IS.ts", dir: "ltr" },
      { code: "it-IT", file: "it-IT.ts", dir: "ltr" },
      { code: "ja-JP", file: "ja-JP.ts", dir: "ltr" },
      { code: "ko-KR", file: "ko-KR.ts", dir: "ltr" },
      { code: "lt-LT", file: "lt-LT.ts", dir: "ltr" },
      { code: "lv-LV", file: "lv-LV.ts", dir: "ltr" },
      { code: "nl-NL", file: "nl-NL.ts", dir: "ltr" },
      { code: "no-NO", file: "no-NO.ts", dir: "ltr" },
      { code: "pl-PL", file: "pl-PL.ts", dir: "ltr" },
      { code: "pt-BR", file: "pt-BR.ts", dir: "ltr" },
      { code: "pt-PT", file: "pt-PT.ts", dir: "ltr" },
      { code: "ro-RO", file: "ro-RO.ts", dir: "ltr" },
      { code: "ru-RU", file: "ru-RU.ts", dir: "ltr" },
      { code: "sk-SK", file: "sk-SK.ts", dir: "ltr" },
      { code: "sl-SI", file: "sl-SI.ts", dir: "ltr" },
      { code: "sr-SP", file: "sr-SP.ts", dir: "ltr" },
      { code: "sv-SE", file: "sv-SE.ts", dir: "ltr" },
      { code: "tr-TR", file: "tr-TR.ts", dir: "ltr" },
      { code: "uk-UA", file: "uk-UA.ts", dir: "ltr" },
      { code: "vi-VN", file: "vi-VN.ts", dir: "ltr" },
      { code: "zh-CN", file: "zh-CN.ts", dir: "ltr" },
      { code: "zh-TW", file: "zh-TW.ts", dir: "ltr" },
      // END: MESSAGE_LOCALES
    ],
    strategy: "no_prefix",
    lazy: true,
    types: "composition",
    langDir: "./../lang/locales", // note: we need to up one ../ because the default root of lang dir is the /frontend/i18n, which can not be configured
    defaultLocale: "en-US",
    detectBrowserLanguage: {
      useCookie: true,
      alwaysRedirect: true,
      fallbackLocale: "en-US",
    },
    compilation: {
      strictMessage: false,
      escapeHtml: true,
    },
    vueI18n: "./../i18n.config.ts", // note: we need to up one ../ because the default root of lang dir is the /frontend/i18n, which can not be configured
  },

  // PWA module configuration: https://vite-pwa-org.netlify.app/frameworks/nuxt.html
  pwa: {
    registerType: "autoUpdate",
    devOptions: {
      enabled: false,
      suppressWarnings: true,
    },
    workbox: {
      navigateFallback: "/",
      globPatterns: ["**/*.{js,css,html,png,svg,ico}"],
      globIgnores: ["404.html", "200.html"],
      cleanupOutdatedCaches: true,
      skipWaiting: true,
      clientsClaim: true,
    },
    client: {
      installPrompt: true,
      periodicSyncForUpdates: 120,
    },
    includeAssets: ["favicon.ico", "apple-touch-icon.png", "safari-pinned-tab.svg"],
    manifest: {
      name: "Mealie",
      short_name: "Mealie",
      id: "/",
      start_url: "/",
      scope: "/",
      display: "standalone",
      background_color: "#FFFFFF",
      theme_color: process.env.THEME_LIGHT_PRIMARY || "#E58325",
      description: "Mealie is a recipe management and meal planning app",
      lang: "en",
      display_override: [
        "standalone",
        "minimal-ui",
        "browser",
        "window-controls-overlay",
      ],
      categories: ["food", "lifestyle"],
      prefer_related_applications: false,
      handle_links: "preferred",
      launch_handler: {
        client_mode: ["focus-existing", "auto"],
      },
      edge_side_panel: {
        preferred_width: 400,
      },
      share_target: {
        action: "/r/create/url",
        method: "GET",
        enctype: "application/x-www-form-urlencoded",
        params: {
          text: "recipe_import_url",
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
          src: "/screenshots/home-narrow.png",
          sizes: "1600x2420",
          form_factor: "narrow",
          label: "Home Page",
        },
        {
          src: "/screenshots/recipe-narrow.png",
          sizes: "1600x2420",
          form_factor: "narrow",
          label: "Recipe Page",
        },
        {
          src: "/screenshots/editor-narrow.png",
          sizes: "1600x2420",
          form_factor: "narrow",
          label: "Editor Page",
        },
        {
          src: "/screenshots/parser-narrow.png",
          sizes: "1600x2420",
          form_factor: "narrow",
          label: "Parser Page",
        },
        {
          src: "/screenshots/home-wide.png",
          sizes: "2560x1460",
          form_factor: "wide",
          label: "Home Page",
        },
        {
          src: "/screenshots/recipe-wide.png",
          sizes: "2560x1460",
          form_factor: "wide",
          label: "Recipe Page",
        },
        {
          src: "/screenshots/editor-wide.png",
          sizes: "2560x1460",
          form_factor: "wide",
          label: "Editor Page",
        },
        {
          src: "/screenshots/parser-wide.png",
          sizes: "2560x1460",
          form_factor: "wide",
          label: "Parser Page",
        },
      ],
      shortcuts: [
        {
          name: "Shopping Lists",
          short_name: "Shopping Lists",
          description: "Open the shopping lists",
          url: "/shopping-lists",
          icons: [
            {
              src: "/icons/mdiFormatListChecks-192x192.png",
              sizes: "192x192",
            },
            {
              src: "/icons/mdiFormatListChecks-96x96.png",
              sizes: "96x96",
            },
          ],
        },
        {
          name: "Meal Planner",
          short_name: "Meal Planner",
          description: "Open the meal planner",
          url: "/household/mealplan/planner/view",
          icons: [
            {
              src: "/icons/mdiCalendarMultiselect-192x192.png",
              sizes: "192x192",
            },
            {
              src: "/icons/mdiCalendarMultiselect-96x96.png",
              sizes: "96x96",
            },
          ],
        },
      ],
    },
  },

  // Vuetify module configuration: https://go.nuxtjs.dev/config-vuetify
  vuetify: {
    moduleOptions: {},
    vuetifyOptions: {
      icons: {
        defaultSet: "mdi-svg",
      },
      // Theme Config set at runtime by /plugins/theme.ts
      // This config doesn't do anything.
      theme: {},
      locale: {
        locale: "en-US",
        fallback: "en-US",
      },
      defaults: {
        VOverlay: {
          scrollStrategy: "close",
        },
        VMenu: {
          scrollStrategy: "close",
        },
        VAutocomplete: {
          scrollStrategy: "close",
        },
        VCombobox: {
          scrollStrategy: "close",
        },
        VSelect: {
          scrollStrategy: "close",
        },
      },
    },
  },
});
