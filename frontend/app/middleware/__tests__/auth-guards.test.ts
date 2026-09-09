import { beforeEach, describe, expect, test, vi } from "vitest";

type Middleware = (to: { fullPath: string; params: Record<string, string> }) => unknown;

const authState = {
  loggedIn: { value: false },
  user: { value: null as { groupSlug?: string } | null },
};

let navigateToMock: ReturnType<typeof vi.fn>;

async function loadMiddleware(path: string): Promise<Middleware> {
  const module = await import(path);
  return module.default;
}

beforeEach(() => {
  vi.resetModules();

  authState.loggedIn.value = false;
  authState.user.value = null;
  navigateToMock = vi.fn(path => path);

  vi.stubGlobal("defineNuxtRouteMiddleware", (middleware: Middleware) => middleware);
  vi.stubGlobal("useMealieAuth", () => authState);
  vi.stubGlobal("navigateTo", navigateToMock);
});

describe("auth-only middleware", () => {
  test("redirects unauthenticated users to login with a return target", async () => {
    const middleware = await loadMiddleware("../auth-only");

    const result = middleware({ fullPath: "/shopping-lists/abc?tab=items", params: {} });

    expect(result).toBe("/login?redirect=%2Fshopping-lists%2Fabc%3Ftab%3Ditems");
    expect(navigateToMock).toHaveBeenCalledWith(
      "/login?redirect=%2Fshopping-lists%2Fabc%3Ftab%3Ditems",
      { redirectCode: 302 },
    );
  });

  test("allows authenticated users through", async () => {
    authState.loggedIn.value = true;
    const middleware = await loadMiddleware("../auth-only");

    const result = middleware({ fullPath: "/shopping-lists/abc", params: {} });

    expect(result).toBeUndefined();
    expect(navigateToMock).not.toHaveBeenCalled();
  });
});

describe("group-only middleware", () => {
  test("redirects unauthenticated users to login with a return target", async () => {
    const middleware = await loadMiddleware("../group-only");

    const result = middleware({ fullPath: "/g/home/recipes/timeline", params: { groupSlug: "home" } });

    expect(result).toBe("/login?redirect=%2Fg%2Fhome%2Frecipes%2Ftimeline");
    expect(navigateToMock).toHaveBeenCalledWith(
      "/login?redirect=%2Fg%2Fhome%2Frecipes%2Ftimeline",
      { redirectCode: 302 },
    );
  });

  test("redirects authenticated users away from other groups", async () => {
    authState.loggedIn.value = true;
    authState.user.value = { groupSlug: "home" };
    const middleware = await loadMiddleware("../group-only");

    const result = middleware({ fullPath: "/g/other/recipes/timeline", params: { groupSlug: "other" } });

    expect(result).toBe("/");
    expect(navigateToMock).toHaveBeenCalledWith("/");
  });

  test("allows authenticated users through for their own group", async () => {
    authState.loggedIn.value = true;
    authState.user.value = { groupSlug: "home" };
    const middleware = await loadMiddleware("../group-only");

    const result = middleware({ fullPath: "/g/home/recipes/timeline", params: { groupSlug: "home" } });

    expect(result).toBeUndefined();
    expect(navigateToMock).not.toHaveBeenCalled();
  });
});
