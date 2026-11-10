import DOMPurify from "isomorphic-dompurify";

const INLINE_ALLOWED_TAGS = ["b", "i", "q", "em", "strong", "sup", "sub", "span"];

/**
 * Sanitizes a short run of inline HTML, such as an ingredient line or a recipe yield, where the
 * only markup we emit is fraction formatting and basic emphasis.
 *
 * Every attribute is dropped, so user text can't bring its own `style`, `class`, or links.
 */
export function sanitizeInlineHtml(rawHtml: string | null | undefined): string {
  if (!rawHtml) {
    return "";
  }

  // Don't add USE_PROFILES here: DOMPurify replaces ALLOWED_TAGS with the whole profile when it's set.
  return DOMPurify.sanitize(rawHtml, {
    ALLOWED_TAGS: INLINE_ALLOWED_TAGS,
    ALLOWED_ATTR: [],
  });
}
