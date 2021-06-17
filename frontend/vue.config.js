const path = require("path");
const manifestJSON = require("./public/manifest.json");
module.exports = {
  transpileDependencies: ["vuetify"],
  publicPath: process.env.NODE_ENV === "production" ? "/" : "/",
  outputDir: process.env.NODE_ENV === "production" ? "./dist" : "../mealie/web",
  devServer: {
    proxy: {
      "/api": {
        target: process.env.VUE_APP_API_BASE_URL,
        secure: false,
      },
    },
  },
  pluginOptions: {
    i18n: {
      locale: "en",
      fallbackLocale: "en",
      localeDir: "locales",
      enableInSFC: true,
    },
    webpackBundleAnalyzer: {
      openAnalyzer: process.env.PREVIEW_BUNDLE,
    },
  },
  configureWebpack: {
    resolve: {
      alias: {
        "@": path.resolve("src"),
      },
    },
  },
  pwa: {
    name: manifestJSON.short_name,
    themeColor: manifestJSON.theme_color,
    msTileColor: manifestJSON.background_color,
    appleMobileWebAppCapable: "yes",
    appleMobileWebAppStatusBarStyle: "black",
    manifestCrossorigin: "use-credentials",

    workboxPluginMode: "InjectManifest",
    workboxOptions: {
      swSrc: "./src/sw.js",
      swDest: "service-worker.js",
    },
  },
};
