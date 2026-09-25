import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { ref } from "vue";

const loggedIn = ref(false);
const navigateTo = vi.fn((to: unknown) => to);

describe("auth middleware", () => {
  beforeEach(() => {
    vi.resetModules();
    navigateTo.mockClear();
    vi.stubGlobal("defineNuxtRouteMiddleware", (fn: unknown) => fn);
    vi.stubGlobal("useMealieAuth", () => ({ loggedIn }));
    vi.stubGlobal("navigateTo", navigateTo);
  });

  afterEach(() => vi.unstubAllGlobals());

  async function run(fullPath: string) {
    const middleware = (await import("../auth")).default as unknown as (to: { fullPath: string }) => unknown;
    return middleware({ fullPath });
  }

  test("sends a logged-out user to the login page and back afterwards", async () => {
    loggedIn.value = false;

    const result = await run("/shopping-lists/abc?foo=bar");

    expect(result).toEqual({ path: "/login", query: { redirect: "/shopping-lists/abc?foo=bar" } });
  });

  test("lets a logged-in user through", async () => {
    loggedIn.value = true;

    const result = await run("/shopping-lists/abc");

    expect(result).toBeUndefined();
    expect(navigateTo).not.toHaveBeenCalled();
  });
});
