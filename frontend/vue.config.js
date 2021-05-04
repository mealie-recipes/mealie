const path = require("path");
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
};
