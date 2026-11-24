import { ESLint } from "eslint";

// Rules that keep raw HTML out of the DOM. Every past HTML-injection bug in the frontend sat behind
// an inline `eslint-disable vue/no-v-html`, so these may only be relaxed by file in eslint.config.mjs.
export const PROTECTED_RULES = new Set([
  "vue/no-v-html",
  "vue/no-restricted-v-bind",
  "vue/no-restricted-syntax",
  "no-restricted-imports",
  "no-restricted-syntax",
]);

/**
 * An ESLint instance that runs only the protected rules and ignores every inline config comment
 * (`eslint-disable*`, `/* eslint rule: off *\/`, ...), so no comment can hide a violation.
 */
export function createSecurityLinter(cwd) {
  return new ESLint({
    cwd,
    overrideConfig: { linterOptions: { noInlineConfig: true, reportUnusedDisableDirectives: "off" } },
    ruleFilter: ({ ruleId }) => PROTECTED_RULES.has(ruleId),
  });
}
