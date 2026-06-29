import DOMPurify from "isomorphic-dompurify";

enum DOMPurifyHook {
  UponSanitizeAttribute = "uponSanitizeAttribute",
  AfterSanitizeAttributes = "afterSanitizeAttributes",
}

const ALLOWED_STYLE_PROPERTIES = [
  "background-color", "color", "font-style", "font-weight", "text-decoration", "text-align",
];

const BASE_ALLOWED_TAGS = [
  "strong", "em", "b", "i", "u", "p", "code", "pre", "samp", "kbd", "var", "sub", "sup", "dfn", "cite",
  "small", "address", "hr", "br", "id", "div", "span", "h1", "h2", "h3", "h4", "h5", "h6",
  "ul", "ol", "li", "dl", "dt", "dd", "abbr", "a", "img", "blockquote",
  "del", "ins", "table", "thead", "tbody", "tfoot", "tr", "th", "td", "colgroup",
];

const BASE_ALLOWED_ATTR = [
  "href", "src", "alt", "height", "width", "class", "title",
  "cite", "datetime", "name", "abbr", "target", "border", "start", "style",
];

// Attributes only meaningful on an <iframe>; added to the allowlist solely when iframe embeds
// are enabled via a configured host allowlist.
const IFRAME_ALLOWED_ATTR = ["allow", "allowfullscreen", "frameborder", "scrolling"];

/**
 * Returns true if an iframe `src` points at one of the allowed hosts. Only https URLs are
 * accepted, and a configured host matches the URL's hostname exactly or as a parent domain
 * (e.g. "youtube.com" matches "www.youtube.com").
 */
function isAllowedIframeSrc(src: string, allowedHosts: string[]): boolean {
  let url: URL;
  try {
    url = new URL(src);
  }
  catch {
    return false;
  }

  if (url.protocol !== "https:") {
    return false;
  }

  const hostname = url.hostname.toLowerCase();
  return allowedHosts.some((host) => {
    const allowed = host.toLowerCase();
    return hostname === allowed || hostname.endsWith(`.${allowed}`);
  });
}

/**
 * Sanitizes pre-rendered HTML (from markdown) for display in user content such as recipe
 * instructions, notes, and descriptions.
 *
 * Only the tags in `BASE_ALLOWED_TAGS` and attributes in `BASE_ALLOWED_ATTR` survive; everything
 * else (scripts, event handlers, form controls, ...) is dropped. `style` attributes are filtered
 * down to the properties in `ALLOWED_STYLE_PROPERTIES`. `<iframe>` is only kept when
 * `allowedIframeHosts` is non-empty, and even then any iframe whose `src` is not an https URL on
 * the host allowlist is removed.
 */
export function sanitizeMarkdownHtml(rawHtml: string | null | undefined, allowedIframeHosts: string[] = []): string {
  if (!rawHtml) {
    return "";
  }

  const allowIframe = allowedIframeHosts.length > 0;

  DOMPurify.addHook(DOMPurifyHook.UponSanitizeAttribute, (_node, data) => {
    if (data.attrName === "style") {
      const styles = data.attrValue.split(";").filter((style) => {
        const [property] = style.split(":");
        return ALLOWED_STYLE_PROPERTIES.includes(property.trim().toLowerCase());
      });
      data.attrValue = styles.join(";");
    }
  });

  if (allowIframe) {
    DOMPurify.addHook(DOMPurifyHook.AfterSanitizeAttributes, (node) => {
      if (node.nodeName === "IFRAME" && !isAllowedIframeSrc(node.getAttribute("src") || "", allowedIframeHosts)) {
        node.parentNode?.removeChild(node);
      }
    });
  }

  const sanitized = DOMPurify.sanitize(rawHtml, {
    ALLOWED_TAGS: allowIframe ? [...BASE_ALLOWED_TAGS, "iframe"] : BASE_ALLOWED_TAGS,
    ALLOWED_ATTR: allowIframe ? [...BASE_ALLOWED_ATTR, ...IFRAME_ALLOWED_ATTR] : BASE_ALLOWED_ATTR,
  });

  Object.values(DOMPurifyHook).forEach((hook) => {
    DOMPurify.removeHook(hook);
  });

  return sanitized;
}
