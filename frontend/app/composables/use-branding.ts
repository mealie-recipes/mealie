/**
 * URLs for the icons generated from a custom logo dropped into the server's data folder.
 * Without one, `brandingUrl` returns null and callers fall back to the built-in Mealie icons.
 */
export function useBranding() {
  const { $appInfo } = useNuxtApp();
  const version = $appInfo?.customLogoVersion;

  function brandingUrl(filename: string): string | null {
    // the version changes with the logo, which lets the server cache these forever
    return version ? `/api/app/about/branding/${filename}?v=${version}` : null;
  }

  return { hasCustomLogo: !!version, brandingUrl };
}
