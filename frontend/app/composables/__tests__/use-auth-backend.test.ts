import { describe, expect, test, vi, beforeEach, afterEach } from "vitest";
// Reused rather than reimplemented: the production reader escapes the full set of regex
// metacharacters, and it has its own coverage in use-token-cookie.test.ts.
import { readTokenCookie } from "../use-token-cookie";

// Pulled in by use-auth-backend purely to wipe cached data on logout. They drag in most of the
// composable graph, none of which this file exercises.
vi.mock("~/composables/store", () => ({ clearAllStores: vi.fn() }));
vi.mock("~/composables/use-clear-composable-caches", () => ({ clearComposableCaches: vi.fn() }));

const TOKEN_NAME = "mealie.access_token";

function encodeToken(payload: Record<string, unknown>): string {
  const body = btoa(JSON.stringify(payload)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  return `header.${body}.signature`;
}

/** A token that expires far enough out that no refresh is scheduled during the test. */
function validToken(): string {
  return encodeToken({ sub: "abc", rme: true, exp: Math.floor(Date.now() / 1000) + 86_400 });
}

function unauthorized() {
  return Object.assign(new Error("Unauthorized"), { response: { status: 401 } });
}

let axiosMock: { get: ReturnType<typeof vi.fn>; post: ReturnType<typeof vi.fn> };
let routerMock: { push: ReturnType<typeof vi.fn> };
let useAuthBackend: typeof import("../use-auth-backend").useAuthBackend;

beforeEach(async () => {
  document.cookie = `${TOKEN_NAME}=; max-age=0`;

  axiosMock = {
    get: vi.fn().mockResolvedValue({ data: { id: "user-1" } }),
    post: vi.fn(),
  };
  routerMock = { push: vi.fn() };

  vi.stubGlobal("useNuxtApp", () => ({ $axios: axiosMock, $appInfo: { production: false } }));
  vi.stubGlobal("useRouter", () => routerMock);
  vi.stubGlobal("useRuntimeConfig", () => ({ public: { AUTH_TOKEN: TOKEN_NAME } }));
  vi.stubGlobal("clearNuxtData", vi.fn());
  vi.stubGlobal("useCookie", (name: string) => ({
    get value() {
      return readTokenCookie(name);
    },
    set value(next: string | null) {
      document.cookie = next === null ? `${name}=; max-age=0` : `${name}=${encodeURIComponent(next)}`;
    },
  }));

  // Module-level refresh state (the in-flight promise, the scheduled timer) would otherwise leak
  // between tests, which is exactly the state these tests are about.
  vi.resetModules();
  ({ useAuthBackend } = await import("../use-auth-backend"));
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("refresh", () => {
  test("shares one request between concurrent callers", async () => {
    const auth = useAuthBackend();
    auth.setToken(validToken());

    let release: (value: unknown) => void = () => {};
    axiosMock.post.mockReturnValue(new Promise(resolve => (release = resolve)));

    const inFlight = [auth.refresh(), auth.refresh(), auth.refresh()];
    release({ data: { access_token: validToken() } });
    await Promise.all(inFlight);

    // Three callers, one round trip — a page load can easily 401 several times at once, and each
    // retrying separately would stampede the endpoint and race over the cookie.
    expect(axiosMock.post).toHaveBeenCalledTimes(1);
    expect(axiosMock.post).toHaveBeenCalledWith("/api/auth/refresh", null, { suppressAlert: true });
  });

  test("allows a new request once the previous one settles", async () => {
    const auth = useAuthBackend();
    auth.setToken(validToken());
    axiosMock.post.mockResolvedValue({ data: { access_token: validToken() } });

    await auth.refresh();
    await auth.refresh();

    expect(axiosMock.post).toHaveBeenCalledTimes(2);
  });

  test("releases the lock after a failure, so the session can still recover", async () => {
    const auth = useAuthBackend();
    auth.setToken(validToken());
    axiosMock.post.mockRejectedValue(new Error("network down"));

    await expect(auth.refresh()).rejects.toThrow("network down");
    await expect(auth.refresh()).rejects.toThrow("network down");

    // A failed refresh must not wedge the lock, or the session can never recover
    expect(axiosMock.post).toHaveBeenCalledTimes(2);
  });

  test("adopts the new token", async () => {
    const auth = useAuthBackend();
    auth.setToken(validToken());

    const replacement = encodeToken({ sub: "abc", rme: true, exp: Math.floor(Date.now() / 1000) + 172_800 });
    axiosMock.post.mockResolvedValue({ data: { access_token: replacement } });

    await auth.refresh();

    expect(auth.token.value).toBe(replacement);
  });

  test("does not reload the session, which would re-enter the interceptor", async () => {
    const auth = useAuthBackend();
    auth.setToken(validToken());
    axiosMock.post.mockResolvedValue({ data: { access_token: validToken() } });

    await auth.refresh();

    // getSession() runs on the same intercepted instance. A 401 there sends the interceptor back
    // into refresh() carrying a fresh config, which the one-retry guard can't recognise, and the
    // cycle starts over. Reloading the user belongs to callers who actually want fresh data.
    expect(axiosMock.get).not.toHaveBeenCalled();
  });

  test("does nothing without a token", async () => {
    const auth = useAuthBackend();

    await auth.refresh();

    expect(axiosMock.post).not.toHaveBeenCalled();
  });

  test("clears the session and redirects when the token is rejected", async () => {
    const auth = useAuthBackend();
    auth.setToken(validToken());
    axiosMock.post.mockRejectedValue(unauthorized());

    await expect(auth.refresh()).rejects.toBeDefined();

    expect(auth.token.value).toBeNull();
    expect(routerMock.push).toHaveBeenCalledWith("/login");
  });

  test("keeps the session on a network failure", async () => {
    const auth = useAuthBackend();
    const token = validToken();
    auth.setToken(token);
    axiosMock.post.mockRejectedValue(new Error("network down"));

    await expect(auth.refresh()).rejects.toThrow();

    // Only auth errors end a session; a blip of connectivity must not log anyone out
    expect(auth.token.value).toBe(token);
    expect(routerMock.push).not.toHaveBeenCalled();
  });
});

describe("signIn", () => {
  test("stores the token and loads the session", async () => {
    const auth = useAuthBackend();
    const token = validToken();
    axiosMock.post.mockResolvedValue({ data: { access_token: token } });

    await auth.signIn(new FormData());

    expect(auth.token.value).toBe(token);
    expect(axiosMock.get).toHaveBeenCalledWith("/api/users/self");
    expect(auth.status.value).toBe("authenticated");
  });

  test("leaves the session unauthenticated when credentials are rejected", async () => {
    const auth = useAuthBackend();
    axiosMock.post.mockRejectedValue(unauthorized());

    await expect(auth.signIn(new FormData())).rejects.toBeDefined();

    expect(auth.status.value).toBe("unauthenticated");
    expect(axiosMock.get).not.toHaveBeenCalled();
  });
});

describe("signOut", () => {
  test("clears the session even when the logout call fails", async () => {
    const auth = useAuthBackend();
    const token = validToken();
    // The server owns this cookie now, so seed it the way a login response would
    document.cookie = `${TOKEN_NAME}=${encodeURIComponent(token)}`;
    auth.setToken(token);
    // The token is often already dead by this point — expired, or invalidated by a password change
    axiosMock.post.mockRejectedValue(unauthorized());

    await auth.signOut();

    expect(auth.token.value).toBeNull();
    expect(readTokenCookie(TOKEN_NAME)).toBeNull();
    expect(routerMock.push).toHaveBeenCalledWith("/login");
  });

  test("honors a callback url", async () => {
    const auth = useAuthBackend();
    auth.setToken(validToken());
    axiosMock.post.mockResolvedValue({ data: {} });

    await auth.signOut("/recipes");

    expect(routerMock.push).toHaveBeenCalledWith("/recipes");
  });
});
