import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { getShareLinkFields, useGroupRecipeActions } from "../use-group-recipe-actions";
import type { GroupRecipeActionOut } from "~/lib/api/types/household";
import type { Recipe } from "~/lib/api/types/recipe";

const createShareToken = vi.fn();
const alertError = vi.fn();

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({
    groupRecipeActions: { getAll: vi.fn().mockResolvedValue({ data: { items: [] } }) },
    recipes: { share: { createOne: createShareToken } },
  }),
}));

vi.mock("../use-toast", () => ({
  alert: { error: (...args: unknown[]) => alertError(...args) },
}));

vi.mock("vue-i18n", async importOriginal => ({
  ...await importOriginal<typeof import("vue-i18n")>(),
  useI18n: () => ({ t: (key: string) => key }),
}));

function createAction(url: string): GroupRecipeActionOut {
  return {
    id: "action-id",
    actionType: "link",
    title: "Action",
    url,
    groupId: "group-id",
    householdId: "household-id",
  };
}

const recipe: Recipe = { id: "recipe-id", slug: "pasta-fagioli" };

describe("getShareLinkFields", () => {
  test("finds a single field", () => {
    expect(getShareLinkFields("https://example.com/?url=${share-link-expires-seconds-300}")).toEqual([
      { field: "${share-link-expires-seconds-300}", seconds: 300 },
    ]);
  });

  test("finds multiple fields and lists a repeated field once", () => {
    const url = "https://example.com/?a=${share-link-expires-seconds-20}&b=${share-link-expires-seconds-60}&c=${share-link-expires-seconds-20}";
    expect(getShareLinkFields(url)).toEqual([
      { field: "${share-link-expires-seconds-20}", seconds: 20 },
      { field: "${share-link-expires-seconds-60}", seconds: 60 },
    ]);
  });

  test.each([
    "https://example.com/?url=${url}",
    "https://example.com/?url=${share-link-expires-seconds-}",
    "https://example.com/?url=${share-link-expires-seconds-abc}",
    "https://example.com/?url=${share-link-expires-seconds--5}",
    "https://example.com/?url=${share-link-expires-seconds-0}",
    "https://example.com/?url=${share-link-expires-seconds-1.5}",
  ])("ignores %s", (url) => {
    expect(getShareLinkFields(url)).toEqual([]);
  });
});

describe("execute", () => {
  let openedTab: { location: { href: string }; focus: ReturnType<typeof vi.fn>; close: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    vi.useFakeTimers({ now: new Date("2026-10-27T12:00:00Z") });
    createShareToken.mockReset();
    alertError.mockReset();
    openedTab = { location: { href: "" }, focus: vi.fn(), close: vi.fn() };
    vi.spyOn(window, "open").mockReturnValue(openedTab as unknown as Window);
    vi.stubGlobal("useRoute", () => ({ params: { groupSlug: "home" } }));
    vi.stubGlobal("useMealieAuth", () => ({ user: ref({ groupSlug: "home" }) }));
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  test("replaces each field with its own share link", async () => {
    createShareToken
      .mockResolvedValueOnce({ data: { id: "token-1" } })
      .mockResolvedValueOnce({ data: { id: "token-2" } });

    const { execute } = useGroupRecipeActions();
    await execute(
      createAction("https://example.com/?a=${share-link-expires-seconds-20}&b=${share-link-expires-seconds-60}&c=${share-link-expires-seconds-20}&slug=${slug}"),
      recipe,
      1,
    );

    expect(createShareToken.mock.calls).toEqual([
      [{ recipeId: "recipe-id", expiresAt: "2026-10-27T12:00:20.000Z" }],
      [{ recipeId: "recipe-id", expiresAt: "2026-10-27T12:01:00.000Z" }],
    ]);
    const origin = window.location.origin;
    expect(openedTab.location.href).toBe(
      `https://example.com/?a=${origin}/g/home/shared/r/token-1&b=${origin}/g/home/shared/r/token-2&c=${origin}/g/home/shared/r/token-1&slug=pasta-fagioli`,
    );
  });

  test("leaves bad values alone and creates no share link", async () => {
    const { execute } = useGroupRecipeActions();
    await execute(createAction("https://example.com/?url=${share-link-expires-seconds-abc}"), recipe, 1);

    expect(createShareToken).not.toHaveBeenCalled();
    expect(window.open).toHaveBeenCalledWith("https://example.com/?url=${share-link-expires-seconds-abc}", "_blank");
  });

  test("falls back to the user's group when the route has none", async () => {
    vi.stubGlobal("useRoute", () => ({ params: {} }));
    createShareToken.mockResolvedValueOnce({ data: { id: "token-1" } });

    const { execute } = useGroupRecipeActions();
    await execute(createAction("https://example.com/?url=${share-link-expires-seconds-300}"), recipe, 1);

    expect(openedTab.location.href).toBe(`https://example.com/?url=${window.location.origin}/g/home/shared/r/token-1`);
  });

  test("closes the tab and shows an error when the expiry is too far out to be a date", async () => {
    const { execute } = useGroupRecipeActions();
    await execute(createAction("https://example.com/?url=${share-link-expires-seconds-99999999999999}"), recipe, 1);

    expect(createShareToken).not.toHaveBeenCalled();
    expect(openedTab.close).toHaveBeenCalled();
    expect(alertError).toHaveBeenCalledWith("events.something-went-wrong");
  });

  test("closes the tab and shows an error when no share link was created", async () => {
    createShareToken.mockResolvedValueOnce({ data: null });

    const { execute } = useGroupRecipeActions();
    await execute(createAction("https://example.com/?url=${share-link-expires-seconds-300}"), recipe, 1);

    expect(openedTab.close).toHaveBeenCalled();
    expect(openedTab.location.href).toBe("");
    expect(alertError).toHaveBeenCalledWith("events.something-went-wrong");
  });
});
