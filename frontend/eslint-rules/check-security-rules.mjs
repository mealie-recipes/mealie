// `pnpm lint:security`: fails when a raw-HTML rule is broken anywhere, even behind an inline disable.
import path from "node:path";
import { createSecurityLinter, PROTECTED_RULES } from "./security.mjs";

const results = await createSecurityLinter(process.cwd()).lintFiles(["."]);

const problems = results.flatMap(result => result.messages
  .filter(message => PROTECTED_RULES.has(message.ruleId))
  .map(message => `${path.relative(process.cwd(), result.filePath)}:${message.line}:${message.column}  ${message.ruleId}  ${message.message}`));

if (problems.length > 0) {
  console.error(problems.join("\n"));
  console.error(
    `\n${problems.length} raw-HTML rule violation(s). These rules ignore inline eslint comments. Render HTML `
    + "with <SafeMarkdown> or <SafeInlineHtml>, or add a reviewed file override in eslint.config.mjs.",
  );
  process.exitCode = 1;
}
