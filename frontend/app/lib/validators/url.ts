/**
 * True only for absolute http(s) URLs. Use it before binding user-supplied URLs to `href` or
 * `src`, since Vue doesn't block `javascript:` or `data:` there.
 */
export function isHttpUrl(value: string | null | undefined): value is string {
  if (!value) {
    return false;
  }

  try {
    const { protocol } = new URL(value);
    return protocol === "http:" || protocol === "https:";
  }
  catch {
    return false;
  }
}
