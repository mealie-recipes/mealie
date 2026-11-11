// @ts-check
import stylistic from "@stylistic/eslint-plugin";
import withNuxt from "./.nuxt/eslint.config.mjs";

const USE_SAFE_COMPONENTS = "Render HTML with <SafeMarkdown> (user text) or <SafeInlineHtml> (app-built markup).";

// Properties and calls that parse a string as HTML.
const HTML_PROPS = "/^(innerHTML|outerHTML|srcdoc)$/";
const HTML_CALLS = "/^(insertAdjacentHTML|createContextualFragment|setHTMLUnsafe|parseHTMLUnsafe)$/";

// Raw-HTML sinks, checked in scripts and (via vue/no-restricted-syntax) in template expressions.
// Rendering goes through the two Safe components, which sanitize with ~/lib/sanitize.
// `pnpm lint:security` enforces these even behind inline eslint comments (see eslint-rules/).
const RAW_HTML_SYNTAX = [
  {
    // .name covers `el.innerHTML`, .value covers `el["innerHTML"]`.
    selector: `AssignmentExpression:matches([left.property.name=${HTML_PROPS}], [left.property.value=${HTML_PROPS}])`,
    message: `Don't assign innerHTML/outerHTML/srcdoc. ${USE_SAFE_COMPONENTS}`,
  },
  {
    // Catches render-function props and template `v-bind="{ innerHTML: x }"`. Constant strings
    // (e.g. the inline head script in nuxt.config.ts) can't carry user input.
    selector: `Property:matches([key.name=${HTML_PROPS}], [key.value=${HTML_PROPS}])`
      + ":not([value.type='Literal'])"
      + ":not([value.type='TemplateLiteral'][value.expressions.length=0])",
    message: `Don't pass a computed innerHTML/outerHTML/srcdoc prop. ${USE_SAFE_COMPONENTS}`,
  },
  {
    selector: `CallExpression:matches([callee.property.name=${HTML_CALLS}], [callee.name=${HTML_CALLS}])`,
    message: `Don't parse HTML strings into the DOM. ${USE_SAFE_COMPONENTS}`,
  },
  {
    selector: "CallExpression[callee.object.name='document'][callee.property.name=/^(write|writeln)$/]",
    message: `Don't use document.write. ${USE_SAFE_COMPONENTS}`,
  },
  {
    // DOMPurify replaces ALLOWED_TAGS with the full profile when USE_PROFILES is set.
    selector: "Property:matches([key.name='USE_PROFILES'], [key.value='USE_PROFILES'])",
    message: "Don't use DOMPurify USE_PROFILES: it overrides ALLOWED_TAGS. Use ~/lib/sanitize.",
  },
];

const SANITIZER_IMPORTS = ["dompurify", "isomorphic-dompurify", "marked"].map(name => ({
  name,
  message: `Import from ~/lib/sanitize instead. ${USE_SAFE_COMPONENTS}`,
}));

export default withNuxt(
  {
    plugins: {
      "@stylistic": stylistic,
    },
    rules: {
      "@stylistic/max-statements-per-line": "off",
      "@stylistic/no-tabs": ["error"],
      "@stylistic/no-mixed-spaces-and-tabs": ["error", "smart-tabs"],
      "@typescript-eslint/no-explicit-any": "off",
      "import/no-extraneous-dependencies": ["error"],
      "vue/first-attribute-linebreak": "error",
      "vue/html-closing-bracket-newline": "error",
      "vue/max-attributes-per-line": [
        "error",
        {
          singleline: 5,
          multiline: 1,
        },
      ],
      "vue/no-mutating-props": "error",
      "vue/no-v-html": "error",
      "vue/no-restricted-v-bind": ["error", {
        argument: `${HTML_PROPS}i`,
        message: USE_SAFE_COMPONENTS,
      }],
      "vue/component-api-style": ["error", ["script-setup"]],
      "no-restricted-syntax": ["error", ...RAW_HTML_SYNTAX],
      "vue/no-restricted-syntax": ["error", ...RAW_HTML_SYNTAX],
      "no-restricted-imports": ["error", { paths: SANITIZER_IMPORTS }],
    },
  },
  {
    files: ["app/lib/sanitize/**"],
    rules: { "no-restricted-imports": "off" },
  },
  {
    files: ["app/components/global/SafeMarkdown.vue", "app/components/global/SafeInlineHtml.vue"],
    rules: { "vue/no-v-html": "off" },
  },
);
