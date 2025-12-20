/**
 * Determine the base URL to use for API requests.
 *
 * On the server, returns BACKEND_URL (trimmed) from environment or "http://localhost:9000" if unset, with any trailing slash removed.
 * In the browser, returns an empty string so relative URLs are used (Next.js rewrites handle routing).
 *
 * @returns The base URL to use for server-side API requests; an empty string when running in the browser.
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
 * Perform a JSON HTTP request against the API with built-in timeout, retry, and unified error messages.
 *
 * @param path - Request path appended to the API base URL; may start with or without a leading `/`.
 * @param init - Optional fetch RequestInit overrides; `Content-Type` defaults to `application/json` and `cache` defaults to `no-store` if not provided.
 * @param options - Optional behavior controls:
 *   - `timeoutMs`: per-request timeout in milliseconds (defaults to NEXT_PUBLIC_API_TIMEOUT_MS or 10000).
 *   - `retries`: number of retry attempts for network errors and 5xx responses (defaults to 3).
 * @returns The parsed JSON response as type `T`.
 * @throws Error when a non-OK HTTP response is received after retries (message includes status and URL), when the response body cannot be parsed as JSON (includes status and a 100-character preview), or when a network/timeout error occurs after all retries (message includes URL and underlying error).
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