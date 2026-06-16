export function getTokenCookieOptions(): Parameters<typeof useCookie>[1] {
  const isSecureConnection = useNuxtApp().$appInfo.production && window?.location?.protocol === "https:";
  return {
    maxAge: useNuxtApp().$appInfo.tokenTime * 60 * 60,
    secure: isSecureConnection,
    sameSite: isSecureConnection ? "none" : "lax",
    partitioned: isSecureConnection,
  };
}
