import { readFileSync } from "fs";
import { resolve } from "path";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { ref } from "vue";

const navigateTo = vi.fn((to: unknown) => to);

describe("can-manage-only middleware", () => {
  beforeEach(() => {
    vi.resetModules();
    navigateTo.mockClear();
    vi.stubGlobal("defineNuxtRouteMiddleware", (fn: unknown) => fn);
    vi.stubGlobal("useMealieAuth", () => ({ user: ref({ canManage: false }) }));
    vi.stubGlobal("navigateTo", navigateTo);
  });

  afterEach(() => vi.unstubAllGlobals());

  async function run() {
    const middleware = (await import("../can-manage-only")).default as unknown as () => unknown;
    return middleware();
  }

  test("redirects a user without canManage to the home page", async () => {
    vi.stubGlobal("useMealieAuth", () => ({ user: ref({ canManage: false }) }));

    await run();

    expect(navigateTo).toHaveBeenCalledWith("/");
  });

  test("lets a user with canManage through", async () => {
    vi.stubGlobal("useMealieAuth", () => ({ user: ref({ canManage: true }) }));

    await run();

    expect(navigateTo).not.toHaveBeenCalled();
  });

  test("redirects when user is null", async () => {
    vi.stubGlobal("useMealieAuth", () => ({ user: ref(null) }));

    await run();

    expect(navigateTo).toHaveBeenCalledWith("/");
  });
});

describe("group data page guard", () => {
  test("data.vue uses can-manage-only middleware to protect /group/data/* routes", () => {
    const dataVuePath = resolve(__dirname, "../../pages/group/data.vue");
    const source = readFileSync(dataVuePath, "utf-8");

    expect(source).toContain("\"can-manage-only\"");
    expect(source).not.toContain("\"can-organize-only\"");
  });
});
