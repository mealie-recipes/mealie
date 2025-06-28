// @ts-check
import stylisticJs from "@stylistic/eslint-plugin-js";
import withNuxt from "./.nuxt/eslint.config.mjs";

export default withNuxt({
  plugins: {
    "@stylistic/js": stylisticJs,
  },
  // Your custom configs here
  rules: {
    "@typescript-eslint/no-explicit-any": "off",
    "vue/no-mutating-props": "warn",
    "vue/no-v-html": "warn",
    "object-curly-newline": "off",
    "consistent-list-newline": "off",
    "vue/first-attribute-linebreak": "off",
    "@stylistic/js/no-tabs": ["error", { allowIndentationTabs: true }],
    "@stylistic/no-tabs": ["error", { allowIndentationTabs: true }],
    "@stylistic/no-mixed-spaces-and-tabs": ["error", "smart-tabs"],
    "vue/max-attributes-per-line": "off",
    "vue/html-indent": "off",
    "vue/html-closing-bracket-newline": "off",
  },
});
