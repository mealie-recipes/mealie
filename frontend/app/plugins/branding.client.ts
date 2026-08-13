import axios from "axios";
import type { AppBranding } from "~/lib/api/types/admin";

export default defineNuxtPlugin({
  async setup() {
    const { data } = await axios.get<AppBranding>("/api/app/about/branding");

    return {
      provide: {
        branding: data,
      },
    };
  },
});
