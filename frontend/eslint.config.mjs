// @ts-check
import stylistic from "@stylistic/eslint-plugin";
import withNuxt from "./.nuxt/eslint.config.mjs";

export default withNuxt({
  plugins: {
    "@stylistic": stylistic,
  },
  rules: {
    "@stylistic/no-tabs": ["error"],
    "@stylistic/no-mixed-spaces-and-tabs": ["error", "smart-tabs"],
    "@typescript-eslint/no-explicit-any": "off",
    "vue/no-mutating-props": "error",
    "vue/no-v-html": "error",
    "vue/first-attribute-linebreak": "off",
    "vue/max-attributes-per-line": "off",
    "vue/html-closing-bracket-newline": "off",
  },
});
