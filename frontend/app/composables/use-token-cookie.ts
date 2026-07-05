export function getTokenCookieOptions() {
  const isSecureConnection = useNuxtApp().$appInfo.production && window?.location?.protocol === "https:";
  return {
    maxAge: useNuxtApp().$appInfo.tokenTime * 60 * 60,
    secure: isSecureConnection,
    sameSite: (isSecureConnection ? "none" : "lax") as "none" | "lax",
    partitioned: isSecureConnection,
  };
}
