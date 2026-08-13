import axios from "axios";
import type { AppBranding } from "~/lib/api/types/admin";

export default defineNuxtPlugin({
  async setup() {
    const { data } = await axios.get<AppBranding>("/api/app/about/branding");

    // ssr is disabled, so the client re-applies the static head config (nuxt.config.ts
    // defaults) on every boot; without this, that reapplication clobbers the branded
    // <title>/favicon that the server already injected into the served HTML.
    useHead({
      title: data.htmlTitle,
      link: data.faviconUrl
        ? [
            { rel: "icon", href: data.faviconUrl },
            { rel: "shortcut icon", href: data.faviconUrl },
          ]
        : [],
    });

    return {
      provide: {
        branding: data,
      },
    };
  },
});
