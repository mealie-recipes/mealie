/**
 * Truncates plain text to `length` characters, appending `clamp` when truncated.
 *
 * The input is treated strictly as text and is never parsed as HTML, so markup in the input is
 * returned verbatim rather than interpreted.
 */
export function truncateText(text: string, length = 20, clamp = "..."): string {
  return text.length > length ? text.slice(0, length) + clamp : text;
}
