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

    iconPaths: {
      favicon32: "./public/img/icons/favicon-32x32.png",
      favicon16: "./public/img/icons/favicon-16x16.png",
      appleTouchIcon: "./public/img/icons/apple-touch-icon-152x152.png",
      maskIcon: "./public/img/icons/safari-pinned-tab.svg",
      msTileImage: "./public/img/icons/msapplication-icon-144x144.png",
    },
    workboxPluginMode: "InjectManifest",
    workboxOptions: {
      swSrc: "./src/sw.js",
      swDest: "service-worker.js",
    },
  },
};
