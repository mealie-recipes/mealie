import { ref } from "@nuxtjs/composition-api";
import { describe, expect, test } from "vitest";
import { usePasswordStrength } from "./use-passwords";

// test("test usePasswordField", () => {
//   const { inputType, togglePasswordShow, passwordIcon } = usePasswordField();
//   expect(inputType.value).toBe("password");
//   expect(passwordIcon.value).toBe("mdi-eye");
//   togglePasswordShow();
//   expect(inputType.value).toBe("text");
//   expect(passwordIcon.value).toBe("mdi-eye-off");
// });

describe("test usePasswordStrength", () => {
  test("weak password", () => {
    const password = ref("123456");
    const { score, strength, color } = usePasswordStrength(password);
    expect(score.value).toBeGreaterThan(0);
    expect(score.value).toBeLessThan(40);
    expect(strength.value).toBe("Weak");
    expect(color.value).toBe("error");
  });

  test("very strong password", () => {
    const password = ref("My~Secret~Not~So~Secret?123");
    const { score, strength, color } = usePasswordStrength(password);
    expect(score.value).toBeGreaterThan(90);
    expect(score.value).toBe(100);
    expect(strength.value).toBe("Very Strong");
    expect(color.value).toBe("success");
  });
});
