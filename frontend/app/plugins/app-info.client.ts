import axios from "axios";
import type { AppInfo } from "~/lib/api/types/admin";

export default defineNuxtPlugin({
  async setup() {
    const { data } = await axios.get<AppInfo>("/api/app/about");

    return {
      provide: {
        appInfo: data,
      },
    };
  },
});
