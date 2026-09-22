import axios from "axios";
import type { AppInfo } from "~/lib/api/types/admin";

export default defineNuxtPlugin({
  async setup() {
    const { data } = await axios.get<AppInfo>("/api/app/about");

    useHead({
      title: data.brandingName,
      link: data.brandingLogoUrl
        ? [
          { rel: "icon", href: data.brandingLogoUrl },
          { rel: "shortcut icon", href: data.brandingLogoUrl },
        ]
        : [],
    });

    return {
      provide: {
        appInfo: data,
      },
    };
  },
});
