import path from "path";
import vue from "@vitejs/plugin-vue";

export default {
  plugins: [vue()],
  test: {
    globals: true,
    environment: "jsdom",
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
