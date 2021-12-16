const path = require("path");
const manifestJSON = require("./public/manifest.json");
const PreloadWebpackPlugin = require("preload-webpack-plugin");

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
      plugins: [new PreloadWebpackPlugin({})],
    },
  },
  pwa: {
    name: manifestJSON.short_name,
    themeColor: manifestJSON.theme_color,
    msTileColor: manifestJSON.theme_color,
    appleMobileWebAppCapable: "yes",
    appleMobileWebAppStatusBarStyle: "black",
    manifestCrossorigin: "use-credentials",

    iconPaths: {
      maskicon: "img/icons/safari-pinned-tab.svg",
      favicon32: "img/icons/favicon-32x32.png",
      favicon16: "img/icons/favicon-16x16.png",
      appleTouchIcon: "img/icons/apple-touch-icon.png",
      msTileImage: "img/icons/mstile-150x150.png",
    },

    workboxPluginMode: "InjectManifest",
    workboxOptions: {
      swSrc: "./src/sw.js",
      swDest: "service-worker.js",
    },
  },
};
