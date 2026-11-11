// @vitest-environment node
import path from "node:path";
import { beforeAll, describe, expect, test } from "vitest";
import { createSecurityLinter, PROTECTED_RULES } from "./security.mjs";

// The same linter `pnpm lint:security` runs: protected rules only, inline config ignored.
const eslint = createSecurityLinter(path.resolve(__dirname, ".."));

async function securityErrors(code: string, filePath: string): Promise<string[]> {
  const [result] = await eslint.lintText(code, { filePath });
  return result!.messages
    .filter(message => message.ruleId && PROTECTED_RULES.has(message.ruleId))
    .map(message => message.ruleId!);
}

const vue = (template: string, script = "const x = \"\";") =>
  `<template>\n  ${template}\n</template>\n\n<script setup lang="ts">\n${script}\n</script>\n`;

const COMPONENT = "app/components/Domain/Foo.vue";
const SCRIPT = "app/composables/foo.ts";

describe("raw HTML lint rules", () => {
  // The first lint loads the whole Nuxt config and its parsers.
  beforeAll(() => securityErrors(vue("<div />"), "app/components/Domain/Warmup.vue"), 60_000);

  test("flags v-html in an ordinary component", async () => {
    expect(await securityErrors(vue("<div v-html=\"x\" />"), COMPONENT)).toEqual(["vue/no-v-html"]);
  });

  test.each(["SafeMarkdown.vue", "SafeInlineHtml.vue"])("allows v-html in %s", async (file) => {
    expect(await securityErrors(vue("<span v-html=\"x\" />"), `app/components/global/${file}`)).toEqual([]);
  });

  test.each([
    [":innerHTML", "<div :innerHTML=\"x\" />", "vue/no-restricted-v-bind"],
    [":srcdoc", "<iframe :srcdoc=\"x\" />", "vue/no-restricted-v-bind"],
    ["object v-bind", "<div v-bind=\"{ innerHTML: x }\" />", "vue/no-restricted-syntax"],
  ])("flags %s in templates", async (_name, template, rule) => {
    expect(await securityErrors(vue(template), COMPONENT)).toEqual([rule]);
  });

  test.each([
    ["document.body.innerHTML = \"x\";"],
    ["document.body[\"outerHTML\"] = \"x\";"],
    ["document.createElement(\"iframe\").srcdoc = \"x\";"],
    ["document.body.insertAdjacentHTML(\"beforeend\", \"x\");"],
    ["document.body.setHTMLUnsafe(\"x\");"],
    ["document.write(\"x\");"],
    ["export const config = { USE_PROFILES: { html: true } };"],
    ["export const f = (x: string) => h(\"div\", { innerHTML: x });"],
    ["export const f = (x: string) => ({ \"innerHTML\": `<b>${x}</b>` });"],
  ])("flags raw HTML sink: %s", async (code) => {
    expect(await securityErrors(`${code}\n`, SCRIPT)).toEqual(["no-restricted-syntax"]);
  });

  test.each([
    ["export const script = { innerHTML: \"console.log(1)\" };"],
    ["export const script = { innerHTML: `console.log(1)` };"],
  ])("allows a constant innerHTML prop: %s", async (code) => {
    expect(await securityErrors(`${code}\n`, SCRIPT)).toEqual([]);
  });

  test.each(["dompurify", "isomorphic-dompurify", "marked"])("restricts importing %s to lib/sanitize", async (pkg) => {
    const code = `import x from "${pkg}";\n\nexport default x;\n`;
    expect(await securityErrors(code, SCRIPT)).toEqual(["no-restricted-imports"]);
    expect(await securityErrors(code, "app/lib/sanitize/foo.ts")).toEqual([]);
  });
});

describe("inline eslint comments can't hide raw HTML rules", () => {
  test.each([
    ["next-line disable", "<div>\n    <!-- eslint-disable-next-line vue/no-v-html -->\n    <div v-html=\"x\" />\n  </div>"],
    ["file-wide disable", "<!-- eslint-disable -->\n  <div v-html=\"x\" />"],
    ["rule config comment", "<!-- eslint vue/no-v-html: \"off\" -->\n  <div v-html=\"x\" />"],
  ])("template %s", async (_name, template) => {
    expect(await securityErrors(vue(template), COMPONENT)).toEqual(["vue/no-v-html"]);
  });

  test.each([
    ["/* eslint-disable */"],
    ["// eslint-disable-next-line no-restricted-syntax -- trust me"],
    ["/* eslint no-restricted-syntax: 0 */"],
  ])("script %s", async (comment) => {
    expect(await securityErrors(`${comment}\ndocument.body.innerHTML = "x";\n`, SCRIPT)).toEqual(["no-restricted-syntax"]);
  });
});
