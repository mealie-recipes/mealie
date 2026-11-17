import { beforeEach, describe, expect, it } from "vitest";
import { nextTick } from "vue";
import { useUserSearchQuery } from "~/composables/use-users/preferences";

describe("useUserSearchQuery", () => {
  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
  });

  it("keeps the recipe filters in localStorage so they survive a browser restart", async () => {
    const query = useUserSearchQuery();
    query.value = { recipe: JSON.stringify({ households: ["7ec68820-709c-4e80-b39e-5c9abd4187d9"] }) };
    await nextTick();

    expect(localStorage.getItem("search-query")).toContain("7ec68820");
    expect(sessionStorage.getItem("search-query")).toBeNull();
  });
});
