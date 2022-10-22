import { expect, test } from "vitest";
import { required, email, whitespace, url, minLength, maxLength } from "./inputs";
export { scorePassword } from "./password";

test("validator required", () => {
  const falsey = "This Field is Required";
  expect(required("123")).toBe(true);
  expect(required("")).toBe(falsey);
  expect(required(undefined)).toBe(falsey);
  expect(required(null)).toBe(falsey);
});

const nulls = [undefined, null];

test("validator email", () => {
  const falsey = "Email Must Be Valid";
  expect(email("123")).toBe(falsey);
  expect(email("email@example.com")).toBe(true);

  for (const n of nulls) {
    expect(email(n)).toBe(falsey);
  }
});

test("whitespace", () => {
  const falsey = "No Whitespace Allowed";
  expect(whitespace("123")).toBe(true);
  expect(whitespace(" ")).toBe(falsey);
  expect(whitespace("123 123")).toBe(falsey);

  for (const n of nulls) {
    expect(whitespace(n)).toBe(falsey);
  }
});

test("url", () => {
  const falsey = "Must Be A Valid URL";
  expect(url("https://example.com")).toBe(true);
  expect(url("")).toBe(falsey);

  for (const n of nulls) {
    expect(url(n)).toBe(falsey);
  }
});

test("minLength", () => {
  const min = 3;
  const falsey = `Must Be At Least ${min} Characters`;
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
  const falsey = `Must Be At Most ${max} Characters`;
  const fn = maxLength(max);
  expect(fn("123")).toBe(true);
  expect(fn("1234")).toBe(falsey);
  expect(fn("")).toBe(true);

  for (const n of nulls) {
    expect(fn(n)).toBe(true);
  }
});
