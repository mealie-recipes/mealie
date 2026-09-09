import { ref } from "vue";
import type { AxiosResponse } from "axios";
import { describe, expect, it, vi } from "vitest";
import { createImageEdit } from "./use-image-edit";
import type { Recipe } from "~/lib/api/types/recipe";

function state() {
  return {
    recipe: ref({ updatedAt: "old", description: "unsaved draft" } as Recipe),
    originalRecipe: ref<Recipe | null>({ updatedAt: "old", description: "original" } as Recipe),
    saving: ref(false),
    saveConflict: ref(false),
  };
}

describe("image edits during a recipe edit", () => {
  it("sends the original version and adopts only the response version without replacing the draft", async () => {
    const s = state();
    const response = { headers: { "x-recipe-updated-at": "new" } } as AxiosResponse;
    const request = vi.fn().mockResolvedValue({ data: { image: "image" }, error: null, response });
    await createImageEdit(s)(request);
    expect(request).toHaveBeenCalledWith({ headers: { "X-Recipe-Updated-At": "old" }, suppressErrorAlertStatuses: [409] });
    expect(s.originalRecipe.value?.updatedAt).toBe("new");
    expect(s.recipe.value.updatedAt).toBe("new");
    expect(s.recipe.value.description).toBe("unsaved draft");
    expect(s.saving.value).toBe(false);
  });

  it("keeps the draft and version and exposes a conflict for a rejected request", async () => {
    const s = state();
    await createImageEdit(s)(vi.fn().mockResolvedValue({ data: null, response: null, error: { response: { status: 409 } } }));
    expect(s.saveConflict.value).toBe(true);
    expect(s.originalRecipe.value?.updatedAt).toBe("old");
    expect(s.recipe.value.description).toBe("unsaved draft");
    expect(s.saving.value).toBe(false);
  });

  it("does not start a second write while saving", async () => {
    const s = state();
    s.saving.value = true;
    const request = vi.fn();
    await createImageEdit(s)(request);
    expect(request).not.toHaveBeenCalled();
  });

  it("releases the saving flag after a transport exception", async () => {
    const s = state();
    await expect(createImageEdit(s)(vi.fn().mockRejectedValue(new Error("offline")))).rejects.toThrow("offline");
    expect(s.saving.value).toBe(false);
    expect(s.originalRecipe.value?.updatedAt).toBe("old");
  });
});
