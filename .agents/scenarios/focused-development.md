# Scenario: focused development and verification

Purpose: make and verify a narrow frontend or backend change without eagerly starting everything.

1. Inspect the relevant code and tests first.
2. Run `.agents/hooks/setup` only when dependencies are required.
3. For Python, run `.agents/hooks/test backend path/to/focused_test.py`.
4. For Vue/TypeScript, run `.agents/hooks/test frontend path/to/changed_file.vue`.
5. Start the stack with `.agents/hooks/resume` only when runtime verification adds evidence.
6. If runtime verification is needed, run `.agents/hooks/verify` and optionally `.agents/hooks/qa`.
7. Run `.agents/hooks/collect` and report the exact checks performed.

This scenario demonstrates the capability model: repository inspection and focused tests do not
pay the startup or Chromium cost unless the change needs them.
