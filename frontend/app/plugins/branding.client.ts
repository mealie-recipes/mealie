// Swap the favicon and home screen icon (keyed in nuxt.config.ts) for the custom logo's icons.
// Runs after app-info.client.ts, which loads $appInfo.
export default defineNuxtPlugin(() => {
  const { brandingUrl } = useBranding();
  const favicon = brandingUrl("favicon.ico");
  if (!favicon) {
    return;
  }

  useHead({
    link: [
      { key: "favicon", rel: "icon", type: "image/x-icon", href: favicon },
      { key: "shortcut-icon", rel: "shortcut icon", type: "image/png", href: brandingUrl("favicon-32x32.png") },
      { key: "apple-touch-icon", rel: "apple-touch-icon", type: "image/png", href: brandingUrl("apple-touch-icon.png") },
    ],
  });
});
