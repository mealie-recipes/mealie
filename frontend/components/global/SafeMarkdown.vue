<template>
  <MDC
    :value="value"
    tag="article"
  />
</template>

<script lang="ts">
import DOMPurify from "isomorphic-dompurify";

export default defineNuxtComponent({
  props: {
    source: {
      type: String,
      default: "",
    },
  },
  setup(props) {
    function sanitizeMarkdown(rawHtml: string | null | undefined): string {
      if (!rawHtml) {
        return "";
      }

      const sanitized = DOMPurify.sanitize(rawHtml, {
        // List based on
        // https://support.zendesk.com/hc/en-us/articles/4408824584602-Allowing-unsafe-HTML-in-help-center-articles
        ALLOWED_TAGS: [
          "strong", "em", "b", "i", "u", "p", "code", "pre", "samp", "kbd", "var", "sub", "sup", "dfn", "cite",
          "small", "address", "hr", "br", "id", "div", "span", "h1", "h2", "h3", "h4", "h5", "h6",
          "ul", "ol", "li", "dl", "dt", "dd", "abbr", "a", "img", "blockquote", "iframe",
          "del", "ins", "table", "thead", "tbody", "tfoot", "tr", "th", "td", "colgroup",
        ],
        ADD_ATTR: [
          "href", "src", "alt", "height", "width", "class", "allow", "title", "allowfullscreen", "frameborder",
          "scrolling", "cite", "datetime", "name", "abbr", "target", "border",
        ],
      });

      return sanitized;
    }

    const value = computed(() => {
      return sanitizeMarkdown(props.source) || "";
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

:deep(th, td) {
  border: 1px solid;
  padding: 8px;
  text-align: left;
}

:deep(th) {
  font-weight: bold;
}
</style>
