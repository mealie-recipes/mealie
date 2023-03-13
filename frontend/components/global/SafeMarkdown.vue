<template>
  <VueMarkdown :source="sanitizeMarkdown(source)"></VueMarkdown>
</template>

<script lang="ts">
// @ts-ignore vue-markdown has no types
import VueMarkdown from "@adapttive/vue-markdown";
import { defineComponent } from "@nuxtjs/composition-api";
import DOMPurify from "isomorphic-dompurify";

export default defineComponent({
  components: {
    VueMarkdown,
  },
  props: {
    source: {
      type: String,
      default: "",
    },
  },
  setup() {
    function sanitizeMarkdown(rawHtml: string | null | undefined): string {
      if (!rawHtml) {
        return "";
      }

      const sanitized = DOMPurify.sanitize(rawHtml, {
        // TODO: some more thought could be put into what is allowed and what isn't
        ALLOWED_TAGS: [
                        "strong", "em", "b", "i", "u", "p", "code", "pre", "samp", "kbd", "var", "sub", "sup", "dfn", "cite",
                        "small", "address", "hr", "br", "id", "div", "span", "h1", "h2", "h3", "h4", "h5", "h6",
                        "ul", "ol", "li", "dl", "dt", "dd", "abbr", "a", "img", "blockquote", "iframe",
                        "del", "ins", "table", "thead", "tbody", "tfoot", "tr", "th", "td", "colgroup",
                      ],
        ADD_ATTR: [
                    "href", "src", "alt", "height", "width", "class", "allow", "title", "allowfullscreen", "frameborder",
                    "scrolling", "style", "cite", "datetime", "name", "abbr", "target", "border",
                  ],
      });

      return sanitized;
    }

    return {
      sanitizeMarkdown,
    };
  },
});
</script>
