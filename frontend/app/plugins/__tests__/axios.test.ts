import type { AxiosInstance, InternalAxiosRequestConfig } from "axios";
import { describe, expect, test, vi, beforeEach, afterEach } from "vitest";

const TOKEN_NAME = "mealie.access_token";
const toastMocks = vi.hoisted(() => ({
  error: vi.fn(),
  info: vi.fn(),
}));

vi.mock("~/composables/use-toast", () => ({
  alert: toastMocks,
}));

/** Rejects the way axios does, so the interceptor sees the config it needs in order to retry. */
function unauthorized(config: InternalAxiosRequestConfig) {
  const error = new Error("Unauthorized") as Error & Record<string, unknown>;
  error.config = config;
  error.response = { status: 401, data: {}, config, headers: {}, statusText: "Unauthorized" };
  error.isAxiosError = true;
  return Promise.reject(error);
}

function ok(config: InternalAxiosRequestConfig) {
  return Promise.resolve({ data: { ok: true }, status: 200, statusText: "OK", headers: {}, config });
}

function unprocessable(config: InternalAxiosRequestConfig, detail: unknown) {
  const error = new Error("Unprocessable Entity") as Error & Record<string, unknown>;
  error.config = config;
  error.response = { status: 422, data: { detail }, config, headers: {}, statusText: "Unprocessable Entity" };
  error.isAxiosError = true;
  return Promise.reject(error);
}

let refreshMock: ReturnType<typeof vi.fn>;
let setTokenMock: ReturnType<typeof vi.fn>;

async function buildClient(adapter: (config: InternalAxiosRequestConfig) => Promise<unknown>) {
  vi.resetModules();
  const plugin = (await import("../axios")).default as unknown as (nuxtApp: {
    runWithContext: <T>(fn: () => T) => T;
  }) => { provide: { axios: AxiosInstance } };

  const { provide } = plugin({ runWithContext: fn => fn() });
  provide.axios.defaults.adapter = adapter as never;
  return provide.axios;
}

beforeEach(() => {
  toastMocks.error.mockClear();
  toastMocks.info.mockClear();
  document.cookie = `${TOKEN_NAME}=a.valid.token`;

  refreshMock = vi.fn().mockResolvedValue(undefined);
  setTokenMock = vi.fn();

  vi.stubGlobal("defineNuxtPlugin", (fn: unknown) => fn);
  vi.stubGlobal("useRuntimeConfig", () => ({ public: { AUTH_TOKEN: TOKEN_NAME } }));
  vi.stubGlobal("useAuthBackend", () => ({ refresh: refreshMock, setToken: setTokenMock }));

  // jsdom refuses real navigation, and the interceptor assigns to location.href on a dead session
  Object.defineProperty(window, "location", {
    value: { pathname: "/g/home/r/soup", search: "", href: "" },
    writable: true,
    configurable: true,
  });
});

afterEach(() => {
  document.cookie = `${TOKEN_NAME}=; max-age=0`;
  vi.unstubAllGlobals();
});

describe("401 handling", () => {
  test("refreshes and replays the original request", async () => {
    const calls: string[] = [];
    const client = await buildClient(async (config) => {
      calls.push(config.url!);
      return calls.length === 1 ? unauthorized(config) : ok(config);
    });

    const response = await client.get("/api/recipes");

    // The whole point: an expiry mid-edit resolves itself instead of throwing the user at /login
    expect(refreshMock).toHaveBeenCalledTimes(1);
    expect(calls).toEqual(["/api/recipes", "/api/recipes"]);
    expect(response.status).toBe(200);
    expect(window.location.href).toBe("");
  });

  test("sends the replay with the refreshed token", async () => {
    const sent: (string | undefined)[] = [];
    refreshMock.mockImplementation(async () => {
      document.cookie = `${TOKEN_NAME}=a.fresh.token`;
    });

    const client = await buildClient(async (config) => {
      sent.push(config.headers.Authorization as string | undefined);
      return sent.length === 1 ? unauthorized(config) : ok(config);
    });

    await client.get("/api/recipes");

    expect(sent).toEqual(["Bearer a.valid.token", "Bearer a.fresh.token"]);
  });

  test("gives up after one retry rather than looping", async () => {
    const client = await buildClient(async config => unauthorized(config));

    await expect(client.get("/api/recipes")).rejects.toBeDefined();

    expect(refreshMock).toHaveBeenCalledTimes(1);
  });

  test("logs out when the refresh itself fails", async () => {
    refreshMock.mockRejectedValue(new Error("session is over"));
    const client = await buildClient(async config => unauthorized(config));

    await expect(client.get("/api/recipes")).rejects.toBeDefined();

    expect(setTokenMock).toHaveBeenCalledWith(null);
    expect(window.location.href).toBe("/login?redirect=%2Fg%2Fhome%2Fr%2Fsoup");
  });

  test.each([
    ["/api/auth/token", "a failed login"],
    ["/api/auth/refresh", "the refresh endpoint itself"],
  ])("never refreshes on %s", async (url) => {
    const client = await buildClient(async config => unauthorized(config));

    await expect(client.post(url)).rejects.toBeDefined();

    expect(refreshMock).not.toHaveBeenCalled();
  });

  test("does not redirect when the logout call is the thing that 401s", async () => {
    const client = await buildClient(async config => unauthorized(config));

    await expect(client.post("/api/auth/logout")).rejects.toBeDefined();

    // signOut does its own SPA redirect. Reloading the page over it would also wipe the toast the
    // preceding request raised, which is how "password updated" used to vanish.
    expect(window.location.href).toBe("");
    expect(refreshMock).not.toHaveBeenCalled();
  });

  test("leaves anonymous callers alone", async () => {
    document.cookie = `${TOKEN_NAME}=; max-age=0`;
    const client = await buildClient(async config => unauthorized(config));

    await expect(client.get("/api/recipes")).rejects.toBeDefined();

    // No token means this is probably just an unauthenticated visitor hitting a guarded route
    expect(refreshMock).not.toHaveBeenCalled();
    expect(window.location.href).toBe("");
  });
});

describe("request headers", () => {
  test("attaches the token as a bearer header", async () => {
    let seen: string | undefined;
    const client = await buildClient(async (config) => {
      seen = config.headers.Authorization as string | undefined;
      return ok(config);
    });

    await client.get("/api/recipes");

    expect(seen).toBe("Bearer a.valid.token");
  });

  test("flags embedded deployments, which the server cannot detect", async () => {
    let seen: unknown;
    const client = await buildClient(async (config) => {
      seen = config.headers["X-Mealie-Embedded"];
      return ok(config);
    });

    const top = window.top;
    Object.defineProperty(window, "top", { value: {}, configurable: true });
    await client.get("/api/recipes");
    Object.defineProperty(window, "top", { value: top, configurable: true });

    expect(seen).toBe("true");
  });
});

describe("error alerts", () => {
  test("shows validation messages returned as a detail array", async () => {
    const client = await buildClient(config => unprocessable(config, [
      { loc: ["body", "tools", 0, "id"], msg: "Field required", type: "missing" },
      { loc: ["body", "tools", 0, "slug"], msg: "Field required", type: "missing" },
    ]));

    await expect(client.put("/api/recipes/test-recipe", {})).rejects.toBeDefined();

    expect(toastMocks.error).toHaveBeenCalledOnce();
    expect(toastMocks.error).toHaveBeenCalledWith("Field required");
  });

  test("preserves structured API error messages", async () => {
    const client = await buildClient(config => unprocessable(config, { message: "Recipe could not be saved" }));

    await expect(client.put("/api/recipes/test-recipe", {})).rejects.toBeDefined();

    expect(toastMocks.error).toHaveBeenCalledWith("Recipe could not be saved");
  });
});
