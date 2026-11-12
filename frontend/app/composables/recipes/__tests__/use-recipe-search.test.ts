import { effectScope, nextTick } from "vue";
import { afterEach, describe, expect, test, vi } from "vitest";
import { useRecipeSearch } from "../use-recipe-search";
import type { UserApi } from "~/lib/api";

const scopes: ReturnType<typeof effectScope>[] = [];
function setup(search = vi.fn().mockResolvedValue({ data: { items: [] }, error: null })) {
  const scope = effectScope();
  scopes.push(scope);
  const result = scope.run(() => useRecipeSearch({ recipes: { search } } as unknown as UserApi))!;
  return { result, search };
}

afterEach(() => {
  scopes.splice(0).forEach(scope => scope.stop());
  vi.useRealTimers();
});

describe("recipe search", () => {
  test("debounces input and sends literal syntax without changes", async () => {
    vi.useFakeTimers();
    const { result, search } = setup();
    result.query.value = "+pork -\"chili peppers\"";
    await nextTick();
    expect(search).not.toHaveBeenCalled();
    await vi.advanceTimersByTimeAsync(500);
    expect(search).toHaveBeenCalledWith(expect.objectContaining({
      search: "+pork -\"chili peppers\"", searchMode: "all", page: 1,
    }));
  });

  test("broadens unchanged syntax and resets mode when text changes", async () => {
    const { result, search } = setup();
    result.query.value = "+pork lettuce wrap -cilantro";
    result.mode.value = "any";
    await result.trigger();
    expect(search).toHaveBeenLastCalledWith(expect.objectContaining({
      search: "+pork lettuce wrap -cilantro", searchMode: "any", page: 1,
    }));
    result.query.value = "chicken";
    expect(result.mode.value).toBe("all");
  });

  test("discards old responses even during the debounce interval", async () => {
    let complete!: (value: unknown) => void;
    const search = vi.fn().mockImplementation(() => new Promise(resolve => complete = resolve));
    const { result } = setup(search);
    result.query.value = "pork";
    const pending = result.trigger();
    result.query.value = "lettuce";
    complete({ data: { items: [{ id: "old" }] }, error: null });
    await pending;
    expect(result.data.value).toEqual([]);
    expect(result.error.value).toBe("");
  });

  test("shows query validation errors and clears old results", async () => {
    const { result } = setup(vi.fn().mockResolvedValue({
      data: null, error: { response: { status: 422 } },
    }));
    result.query.value = "\"unfinished";
    await result.trigger();
    expect(result.error.value).toBe("search.invalid-query");
    expect(result.data.value).toEqual([]);
    expect(result.loading.value).toBe(false);
  });
});
