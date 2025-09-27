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
  },
});
