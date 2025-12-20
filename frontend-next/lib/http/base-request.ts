/**
 * Get the base URL for API requests
 * Server-side: use BACKEND_URL env var or localhost
 * Client-side: use relative URLs (handled by Next.js rewrites)
 * @returns Base URL as string for server-side, empty string for client-side
 */
export function getApiBaseUrl(): string {
  // Server-side: use backend URL from environment
  if (typeof window === "undefined") {
    const rawUrl = process.env.BACKEND_URL || "http://localhost:9000";
    const backendUrl = rawUrl.trim();
    return backendUrl.endsWith("/") ? backendUrl.slice(0, -1) : backendUrl;
  }
  // Client-side: use relative URLs (Next.js rewrites handle routing)
  return "";
}

/**
 * Base JSON request with timeout, retry, and consistent errors.
 */
export async function baseRequest<T>(
  path: string,
  init?: RequestInit,
  options?: { timeoutMs?: number; retries?: number }
): Promise<T> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}${path.startsWith("/") ? path : `/${path}`}`;

  const timeoutMs =
    options?.timeoutMs ??
    Number(process.env.NEXT_PUBLIC_API_TIMEOUT_MS ?? 10000);
  const retries = Math.max(0, options?.retries ?? 3);

  let attempt = 0;
  while (true) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const headers = new Headers(init?.headers as HeadersInit);
      if (!headers.has("Content-Type"))
        headers.set("Content-Type", "application/json");

      const response = await fetch(url, {
        ...init,
        headers,
        signal: controller.signal,
        cache: init?.cache ?? "no-store",
      });

      if (!response.ok) {
        if (
          response.status >= 500 &&
          response.status < 600 &&
          attempt < retries
        ) {
          attempt += 1;
          const backoff = 250 * attempt;
          await new Promise((r) => setTimeout(r, backoff));
          continue;
        }
        throw new Error(
          `Request failed: ${response.status} ${response.statusText} (${url})`
        );
      }

      const text = await response.text();
      try {
        // Try to parse JSON
        return JSON.parse(text) as T;
      } catch (err) {
        throw new Error(
          `Invalid JSON received from ${url} (Status: ${
            response.status
          }). \nPreview: ${text.substring(0, 100)}...`
        );
      }
    } catch (err: unknown) {
      const isAbort = err instanceof Error && err.name === "AbortError";
      const isNetwork = err instanceof TypeError;
      if ((isAbort || isNetwork) && attempt < retries) {
        attempt += 1;
        const backoff = 250 * attempt;
        await new Promise((r) => setTimeout(r, backoff));
        continue;
      }
      const message = err instanceof Error ? err.message : String(err);
      throw new Error(`Network error fetching ${url}: ${message}`);
    } finally {
      clearTimeout(timeoutId);
    }
  }
}
