<template>
  <!-- eslint-disable-next-line vue/no-v-html is safe here because all HTML is sanitized with DOMPurify in setup() -->
  <div v-html="value" />
</template>

<script lang="ts">
import DOMPurify from "isomorphic-dompurify";
import { marked } from "marked";

enum DOMPurifyHook {
  UponSanitizeAttribute = "uponSanitizeAttribute",
}

export default defineNuxtComponent({
  props: {
    source: {
      type: String,
      default: "",
    },
  },
  setup(props) {
    const ALLOWED_STYLE_TAGS = [
      "background-color", "color", "font-style", "font-weight", "text-decoration", "text-align",
    ];

    function sanitizeMarkdown(rawHtml: string | null | undefined): string {
      if (!rawHtml) {
        return "";
      }

      DOMPurify.addHook(DOMPurifyHook.UponSanitizeAttribute, (node, data) => {
        if (data.attrName === "style") {
          const styles = data.attrValue.split(";").filter((style) => {
            const [property] = style.split(":");
            return ALLOWED_STYLE_TAGS.includes(property.trim().toLowerCase());
          });
          data.attrValue = styles.join(";");
        }
      });

      const sanitized = DOMPurify.sanitize(rawHtml, {
        ALLOWED_TAGS: [
          "strong", "em", "b", "i", "u", "p", "code", "pre", "samp", "kbd", "var", "sub", "sup", "dfn", "cite",
          "small", "address", "hr", "br", "id", "div", "span", "h1", "h2", "h3", "h4", "h5", "h6",
          "ul", "ol", "li", "dl", "dt", "dd", "abbr", "a", "img", "blockquote", "iframe",
          "del", "ins", "table", "thead", "tbody", "tfoot", "tr", "th", "td", "colgroup",
        ],
        ALLOWED_ATTR: [
          "href", "src", "alt", "height", "width", "class", "allow", "title", "allowfullscreen", "frameborder",
          "scrolling", "cite", "datetime", "name", "abbr", "target", "border", "start", "style",
        ],
      });

      Object.values(DOMPurifyHook).forEach((hook) => {
        DOMPurify.removeHook(hook);
      });

      return sanitized;
    }

    const value = computed(() => {
      const rawHtml = marked.parse(props.source || "", { async: false, breaks: true });
      return sanitizeMarkdown(rawHtml);
    });

    return {
      value,
    };
  },
});
</script>

<style scoped>
:deep(table) {
  border-collapse: collapse;
  width: 100%;
}

:deep(th),
:deep(td) {
  border: 1px solid;
  padding: 8px;
  text-align: left;
}

:deep(th) {
  font-weight: bold;
}

:deep(ul),
:deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}
</style>
