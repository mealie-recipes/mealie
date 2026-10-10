import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { ref } from "vue";

const REDIRECT = "/";
const navigateTo = vi.fn((to: unknown) => ({ redirected: true, to }));

// ---------------------------------------------------------------------------
// Table-driven helper: each entry describes one middleware under test.
// ---------------------------------------------------------------------------
type MiddlewareCase = {
  name: string;
  path: string;
  // user object when the user is NOT allowed through
  blockedUser: Record<string, unknown> | null;
  // user object when the user IS allowed through
  allowedUser: Record<string, unknown>;
  // for middlewares that receive a route argument (e.g. group-only)
  routeArg?: unknown;
  allowedRouteArg?: unknown;
};

const cases: MiddlewareCase[] = [
  {
    name: "can-organize-only",
    path: "../can-organize-only",
    blockedUser: { canOrganize: false },
    allowedUser: { canOrganize: true },
  },
  {
    name: "can-manage-only",
    path: "../can-manage-only",
    blockedUser: { canManage: false },
    allowedUser: { canManage: true },
  },
  {
    name: "admin-only",
    path: "../admin-only",
    blockedUser: { admin: false },
    allowedUser: { admin: true },
  },
  {
    name: "advanced-only",
    path: "../advanced-only",
    blockedUser: { advanced: false },
    allowedUser: { advanced: true },
  },
  {
    name: "can-manage-household-only",
    path: "../can-manage-household-only",
    blockedUser: { canManageHousehold: false },
    allowedUser: { canManageHousehold: true },
  },
  {
    name: "group-only",
    path: "../group-only",
    blockedUser: { groupSlug: "group-a" },
    allowedUser: { groupSlug: "group-a" },
    routeArg: { params: { groupSlug: "group-b" } },
    allowedRouteArg: { params: { groupSlug: "group-a" } },
  },
];

describe("permission middlewares return their redirect", () => {
  beforeEach(() => {
    vi.resetModules();
    navigateTo.mockClear();
    vi.stubGlobal("defineNuxtRouteMiddleware", (fn: unknown) => fn);
    vi.stubGlobal("navigateTo", navigateTo);
  });

  afterEach(() => vi.unstubAllGlobals());

  for (const c of cases) {
    describe(c.name, () => {
      async function load() {
        const mod = await import(c.path);
        return mod.default as (to?: unknown) => unknown;
      }

      test("RETURNS the redirect for a user without permission", async () => {
        vi.stubGlobal("useMealieAuth", () => ({ user: ref(c.blockedUser), loggedIn: ref(true) }));
        const mw = await load();
        const result = mw(c.routeArg ?? {});
        expect(navigateTo).toHaveBeenCalledWith(REDIRECT);
        expect(result).toEqual({ redirected: true, to: REDIRECT });
      });

      test("RETURNS the redirect when user is null", async () => {
        vi.stubGlobal("useMealieAuth", () => ({ user: ref(null), loggedIn: ref(true) }));
        const mw = await load();
        const result = mw(c.routeArg ?? {});
        expect(navigateTo).toHaveBeenCalledWith(REDIRECT);
        expect(result).toEqual({ redirected: true, to: REDIRECT });
      });

      test("returns undefined (lets through) for an allowed user", async () => {
        vi.stubGlobal("useMealieAuth", () => ({ user: ref(c.allowedUser), loggedIn: ref(true) }));
        const mw = await load();
        const result = mw(c.allowedRouteArg ?? c.routeArg ?? {});
        expect(navigateTo).not.toHaveBeenCalled();
        expect(result).toBeUndefined();
      });
    });
  }
});
