module.exports = {
  transpileDependencies: ["vuetify"],
  publicPath: process.env.NODE_ENV === "production" ? "/static/" : "/",
  outputDir: process.env.NODE_ENV === "production" ? "./dist" : "../mealie/web",
  devServer: {
    proxy: {
      "/api": {
        target: "http://mealie-api:9000 ",
        secure: false,
      },
    },
  },
  pluginOptions: {
    i18n: {
      locale: 'en',
      fallbackLocale: 'en',
      localeDir: 'locales',
      enableInSFC: true
    }
  }
};
