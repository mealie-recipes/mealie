import { ref } from "vue";
import { describe, expect, test } from "vitest";
import { usePasswordStrength } from "./use-passwords";
import { stubI18n } from "~/tests/utils";

describe("test usePasswordStrength", () => {
  test("weak password", () => {
    const pw = ref("123456");

    const result = usePasswordStrength(pw, stubI18n());
    const { score, strength, color } = result;

    expect(score.value).toBeGreaterThan(0);
    expect(score.value).toBeLessThan(40);
    expect(strength.value).toBe("Weak");
    expect(color.value).toBe("error");
  });

  test("very strong password", () => {
    const password = ref("My~Secret~Not~So~Secret?123");
    const { score, strength, color } = usePasswordStrength(password, stubI18n());
    expect(score.value).toBeGreaterThan(90);
    expect(score.value).toBe(100);
    expect(strength.value).toBe("Very Strong");
    expect(color.value).toBe("success");
  });
});
