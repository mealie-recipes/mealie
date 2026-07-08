export function getTokenCookieOptions() {
  const { $appInfo } = useNuxtApp();

  const isSecureConnection = $appInfo.production && window?.location?.protocol === "https:";
  const isEmbedded = isSecureConnection && window?.self !== window?.top;

  return {
    maxAge: $appInfo.tokenTime * 60 * 60,
    secure: isSecureConnection,
    sameSite: (isEmbedded ? "none" : "lax") as "none" | "lax",
    partitioned: isEmbedded,
  };
}
