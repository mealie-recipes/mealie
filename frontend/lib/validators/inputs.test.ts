import { expect, test, vi } from "vitest";
import enUS from "~/lang/messages/en-US.json";

import { required, email, whitespace, url, minLength, maxLength } from "./inputs";

vi.mock("~/composables/use-global-i18n", () => {
  const interpolate = (msg: string, params?: Record<string, unknown>) => {
    if (!params) return msg;
    return msg
      .replace("{min}", String(params.min ?? ""))
      .replace("{max}", String(params.max ?? ""));
  };

  const t = (key: string, params?: Record<string, unknown>) => {
    const parts = key.split(".");
    let acc: any = enUS as any;
    for (const p of parts) acc = acc?.[p];
    const msg: string | undefined = acc;
    return interpolate(msg ?? key, params);
  };

  return { useGlobalI18n: () => ({ t }) };
});

export { scorePassword } from "./password";

// Tests

test("validator required", () => {
  const falsey = enUS.validators.required;
  expect(required("123")).toBe(true);
  expect(required("")).toBe(falsey);
  expect(required(undefined)).toBe(falsey);
  expect(required(null)).toBe(falsey);
});

const nulls = [undefined, null];

test("validator email", () => {
  const falsey = enUS.validators["invalid-email"];
  expect(email("123")).toBe(falsey);
  expect(email("email@example.com")).toBe(true);

  for (const n of nulls) {
    expect(email(n)).toBe(falsey);
  }
});

test("whitespace", () => {
  const falsey = enUS.validators["no-whitespace"];
  expect(whitespace("123")).toBe(true);
  expect(whitespace(" ")).toBe(falsey);
  expect(whitespace("123 123")).toBe(falsey);

  for (const n of nulls) {
    expect(whitespace(n)).toBe(falsey);
  }
});

test("url", () => {
  const falsey = enUS.validators["invalid-url"];
  expect(url("https://example.com")).toBe(true);
  expect(url("")).toBe(falsey);

  for (const n of nulls) {
    expect(url(n)).toBe(falsey);
  }
});

test("minLength", () => {
  const min = 3;
  const falsey = enUS.validators["min-length"].replace("{min}", String(min));
  const fn = minLength(min);
  expect(fn("123")).toBe(true);
  expect(fn("12")).toBe(falsey);
  expect(fn("")).toBe(falsey);

  for (const n of nulls) {
    expect(fn(n)).toBe(falsey);
  }
});

test("maxLength", () => {
  const max = 3;
  const falsey = enUS.validators["max-length"].replace("{max}", String(max));
  const fn = maxLength(max);
  expect(fn("123")).toBe(true);
  expect(fn("1234")).toBe(falsey);
  expect(fn("")).toBe(true);

  for (const n of nulls) {
    expect(fn(n)).toBe(true);
  }
});
