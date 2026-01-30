<template>
  <!-- eslint-disable-next-line vue/no-v-html is safe here because all HTML is sanitized with DOMPurify in setup() -->
  <div v-html="value" />
</template>

<script lang="ts">
import DOMPurify from "isomorphic-dompurify";
import { marked } from "marked";

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
        ALLOWED_ATTR: [
          "href", "src", "alt", "height", "width", "class", "allow", "title", "allowfullscreen", "frameborder",
          "scrolling", "cite", "datetime", "name", "abbr", "target", "border", "start",
        ],
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
