import { afterEach, describe, expect, test, vi } from "vitest";
import type { Composer } from "vue-i18n";
import { useRequests } from "../api-client";

describe("useRequests", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("passes the request config to DELETE requests", async () => {
    const axiosDelete = vi.fn().mockResolvedValue({ data: null });
    vi.stubGlobal("useNuxtApp", () => ({
      $axios: { delete: axiosDelete, defaults: { headers: { common: {} } } },
    }));
    const i18n = { locale: { value: "en-US" } } as unknown as Composer;

    await useRequests(i18n).delete("/api/foods/1", { suppressAlert: true });

    expect(axiosDelete).toHaveBeenCalledExactlyOnceWith("/api/foods/1", { suppressAlert: true });
  });
});
