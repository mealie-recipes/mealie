import path from "path";
import vue from "@vitejs/plugin-vue";
import AutoImport from "unplugin-auto-import/vite";

export default {
  plugins: [
    vue(),
    AutoImport({
      imports: ["vue", "@vueuse/core", "vue-i18n"],
      dts: false,
    }),
  ],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./app/tests/setup.ts"],
    coverage: {
      provider: "v8",
      include: ["app/{lib,components,composables,layouts,pages}/**/*.{ts,tsx,vue}"],
      exclude: ["**/*.test.*", "node_modules/**", "dist/**", "coverage/**", "**/__tests__/**"],
      reporter: ["html", "text-summary"],
      all: true,
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./app"),
      "~": path.resolve(__dirname, "./app"),
      "@@": path.resolve(__dirname, "."),
      "~~": path.resolve(__dirname, "."),
    },
  },
};
