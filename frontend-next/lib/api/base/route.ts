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
 * Builds a URL from a path plus optional query parameters and optional host/prefix configuration.
 *
 * Constructs a URL by combining the configured or provided host and prefix with `rest`, appends any
 * query parameters from `params` (array values produce multiple entries with the same key), and
 * removes the DEFAULT_HOST substring from the final string if present.
 *
 * @param rest - The path portion to append to the configured prefix and host (e.g., "/users").
 * @param params - An object mapping query parameter names to values; values may be strings, numbers, booleans, `null`, `undefined`, or arrays of those types. Pass `null` to omit query parameters.
 * @param options - Optional overrides.
 * @param options.host - Host to use instead of the default host.
 * @param options.prefix - Prefix to prepend to `rest` (for example a versioned API prefix).
 * @returns The resulting URL as a string, with the default host removed if it appears in the output.
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
 * Create a route builder bound to a specific host and prefix.
 *
 * @param host - Base host to use when constructing routes (e.g., "https://api.example.com")
 * @param prefix - Optional path prefix to prepend to each route (e.g., "/v1")
 * @returns A function that builds a URL string for a given path and optional query parameters
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