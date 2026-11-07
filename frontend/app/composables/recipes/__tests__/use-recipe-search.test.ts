import { describe, expect, test, vi } from "vitest";
import { effectScope } from "vue";
import { useRecipeSearch } from "../use-recipe-search";
import type { UserApi } from "~/lib/api";
import type { Recipe } from "~/lib/api/types/recipe";

function deferred<T>() {
  let resolve!: (value: T) => void;

  const promise = new Promise<T>((resolvePromise) => {
    resolve = resolvePromise;
  });

  return { promise, resolve };
}

describe("useRecipeSearch", () => {
  test("does not overwrite newer results when an older search finishes last", async () => {
    const olderRequest = deferred<unknown>();
    const newerRequest = deferred<unknown>();

    const search = vi
      .fn()
      .mockReturnValueOnce(olderRequest.promise)
      .mockReturnValueOnce(newerRequest.promise);

    const api = {
      recipes: { search },
    } as unknown as UserApi;

    const scope = effectScope();
    const searchState = scope.run(() => useRecipeSearch(api))!;

    try {
      const chickenRecipe = { id: "chicken" } as unknown as Recipe;
      const pastaRecipe = { id: "pasta" } as unknown as Recipe;

      searchState.query.value = "chicken";
      const firstSearch = searchState.trigger();

      searchState.query.value = "pasta";
      const secondSearch = searchState.trigger();

      // The newer search finishes first.
      newerRequest.resolve({
        data: { items: [pastaRecipe] },
        error: null,
      });

      await secondSearch;

      expect(searchState.data.value).toEqual([pastaRecipe]);
      expect(searchState.loading.value).toBe(false);

      // The older search finishes afterward.
      olderRequest.resolve({
        data: { items: [chickenRecipe] },
        error: null,
      });

      await firstSearch;

      // The older response must not replace the newer results.
      expect(searchState.data.value).toEqual([pastaRecipe]);
      expect(searchState.loading.value).toBe(false);
    } finally {
      scope.stop();
    }
  });

  test("does not let an older failed search clear newer results", async () => {
    const olderRequest = deferred<any>();
    const newerRequest = deferred<any>();

    const search = vi
      .fn()
      .mockReturnValueOnce(olderRequest.promise)
      .mockReturnValueOnce(newerRequest.promise);

    const api = {
      recipes: { search },
    } as unknown as UserApi;

    const scope = effectScope();
    const searchState = scope.run(() => useRecipeSearch(api))!;

    try {
      const pastaRecipe = { id: "pasta" } as unknown as Recipe;

      searchState.query.value = "chicken";
      const firstSearch = searchState.trigger();

      searchState.query.value = "pasta";
      const secondSearch = searchState.trigger();

      newerRequest.resolve({
        data: { items: [pastaRecipe] },
        error: null,
      });

      await secondSearch;

      // The older request fails after the newer request succeeds.
      olderRequest.resolve({
        data: null,
        error: new Error("Older request failed"),
      });

      await firstSearch;

      expect(searchState.data.value).toEqual([pastaRecipe]);
      expect(searchState.loading.value).toBe(false);
    } finally {
      scope.stop();
    }
  });
});
