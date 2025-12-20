export type QueryValue =
  | string
  | string[]
  | number
  | number[]
  | boolean
  | null
  | undefined;

const DEFAULT_HOST = "http://localhost.com";
const DEFAULT_PREFIX = "";

/**
 * route is the main URL builder for the API. It will use the provided host and prefix
 * (or defaults) and then append the passed in path parameter using the `URL` class from the
 * browser. It will also append any query parameters passed in as the second parameter.
 *
 * The default host `http://localhost.com` is removed from the path if it is present. This allows us
 * to bootstrap the API with different hosts as needed (like for testing) but still allows us to use
 * relative URLs in production because the API and client bundle are served from the same server/host.
 *
 * This implementation is thread-safe and avoids race conditions in concurrent Next.js requests.
 */
export function route(
  rest: string,
  params: Record<string, QueryValue> | null = null,
  options?: { host?: string; prefix?: string }
): string {
  const host = options?.host ?? DEFAULT_HOST;
  const prefix = options?.prefix ?? DEFAULT_PREFIX;

  const url = new URL(prefix + rest, host);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (Array.isArray(value)) {
        for (const item of value) {
          url.searchParams.append(key, String(item));
        }
      } else {
        url.searchParams.append(key, String(value));
      }
    }
  }

  return url.toString().replace(DEFAULT_HOST, "");
}

/**
 * Factory function to create a route builder with pre-configured host and prefix.
 * This is useful when you need to create multiple routes with the same configuration
 * without repeating the options parameter.
 *
 * @example
 * const apiRoute = createRoute("https://api.example.com", "/v1");
 * const url = apiRoute("/users", { page: 1 });
 */
export function createRoute(host: string, prefix: string = "") {
  return (
    rest: string,
    params: Record<string, QueryValue> | null = null
  ): string => {
    return route(rest, params, { host, prefix });
  };
}
