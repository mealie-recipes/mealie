import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createRecipeFile, downloadRecipeFile, shareRecipeFile } from "./recipe-file";

function readFile(file: File): Promise<string> {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.readAsText(file);
  });
}

const recipe = {
  id: "recipe-id", name: "Lentil soup", slug: "lentil-soup", description: "A recipe",
  recipeIngredient: [{ note: "1 cup lentils", quantity: 1, food: { name: "lentils", extras: { private: "secret" }, groupId: "private" } }],
  recipeInstructions: [{ text: "Simmer", ingredientReferences: ["lentils"] }],
  prepTime: "10 minutes", cookTime: "20 minutes", totalTime: "30 minutes",
  notes: [{ title: "Tip", text: "Stir" }], nutrition: { calories: "100" },
  userId: "private", householdId: "private", groupId: "private",
  comments: [{ user: { email: "private@example.com" } }],
  extras: { token: "secret" }, settings: { public: false }, token: "secret",
};

beforeEach(() => {
  vi.stubGlobal("isSecureContext", true);
  vi.stubGlobal("navigator", { canShare: vi.fn(() => true), share: vi.fn().mockResolvedValue(undefined) });
});
afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks(); vi.useRealTimers(); });

describe("recipe file", () => {
  it("preserves recipe content in Mealie JSON without account or unrelated metadata", async () => {
    const file = createRecipeFile(recipe, recipe.slug);
    expect(file.name).toBe("lentil-soup.json");
    expect(file.type).toBe("application/json");
    const exported = JSON.parse(await readFile(file));
    expect(exported.recipeInstructions).toEqual(recipe.recipeInstructions);
    expect(exported.totalTime).toBe(recipe.totalTime);
    expect(exported.id).toBe(recipe.id);
    expect(exported.notes).toEqual(recipe.notes);
    expect(exported.nutrition).toEqual(recipe.nutrition);
    expect(exported.recipeIngredient[0].food).toEqual({ name: "lentils" });
    expect(JSON.stringify(exported)).not.toMatch(/private|secret|token/);
  });

  it("preserves structured recipe seconds without interpreting instruction timing", async () => {
    const content = { ...recipe, totalTimeSeconds: 1800, prepTimeSeconds: 600, performTimeSeconds: 1200,
      recipeInstructions: [{ id: "step", text: "Simmer", futureTimingField: 90 }] };
    const exported = JSON.parse(await readFile(createRecipeFile(content, recipe.slug)));
    expect(exported.totalTimeSeconds).toBe(1800);
    expect(exported.prepTimeSeconds).toBe(600);
    expect(exported.performTimeSeconds).toBe(1200);
    expect(exported.recipeInstructions).toEqual(content.recipeInstructions);
  });

  it("projects full referenced recipes recursively without leaking private export fields", async () => {
    const privateRecipe = {
      comments: [{ text: "PRIVATE", user: { email: "PRIVATE@example.invalid" } }],
      settings: { public: false }, assets: [{ fileName: "PRIVATE.pdf" }], image: "PRIVATE",
      rating: 4, lastMade: "2026-01-01", dateAdded: "2026-01-01", dateUpdated: "2026-01-01",
      userId: "PRIVATE", householdId: "PRIVATE", groupId: "PRIVATE", extras: { secret: "PRIVATE" },
    };
    const leaf = {
      ...privateRecipe, id: "leaf-id", name: "Stock", slug: "stock", description: "Vegetable stock",
      totalTimeSeconds: 1800, prepTimeSeconds: 600, performTimeSeconds: 1200,
      recipeIngredient: [{ referenceId: "stock-ingredient", note: "Water", referencedRecipe: null }],
      recipeInstructions: [{ id: "stock-step", text: "Simmer", ingredientReferences: [{ referenceId: "stock-ingredient" }] }],
      nutrition: { calories: "10" }, notes: [{ title: "Tip", text: "Stir" }],
    };
    const nested = {
      ...leaf, id: "nested-id", name: "Sauce",
      recipeIngredient: [{ referenceId: "sauce-ingredient", quantity: 2, referencedRecipe: leaf }],
    };
    const content = { ...recipe, recipeIngredient: [{ referenceId: "outer-ingredient", referencedRecipe: nested }] };
    const before = JSON.stringify(content);
    const exported = JSON.parse(await readFile(createRecipeFile(content, recipe.slug)));
    const nestedExport = exported.recipeIngredient[0].referencedRecipe;
    const leafExport = nestedExport.recipeIngredient[0].referencedRecipe;
    for (const projected of [nestedExport, leafExport]) {
      for (const key of Object.keys(privateRecipe)) expect(projected).not.toHaveProperty(key);
      expect(projected.totalTimeSeconds).toBe(1800);
      expect(projected.prepTimeSeconds).toBe(600);
      expect(projected.performTimeSeconds).toBe(1200);
      expect(projected.recipeInstructions).toEqual(leaf.recipeInstructions);
      expect(projected.nutrition).toEqual(leaf.nutrition);
      expect(projected.notes).toEqual(leaf.notes);
    }
    expect(nestedExport.id).toBe("nested-id");
    expect(nestedExport.recipeIngredient[0].referenceId).toBe("sauce-ingredient");
    expect(nestedExport.recipeIngredient[0].quantity).toBe(2);
    expect(leafExport.id).toBe("leaf-id");
    expect(leafExport.name).toBe("Stock");
    expect(leafExport.recipeIngredient).toEqual(leaf.recipeIngredient);
    expect(JSON.stringify(exported)).not.toContain("PRIVATE");
    expect(JSON.stringify(content)).toBe(before);
  });

  it("removes household memberships from tools and foods at every recipe depth", async () => {
    const food = { id: "food-id", name: "lentils", householdsWithIngredientFood: ["PRIVATE-household"] };
    const tool = { id: "tool-id", name: "pot", householdsWithTool: ["PRIVATE-household"] };
    const nested = { id: "nested-id", tools: [tool], recipeIngredient: [{ food, referencedRecipe: null }] };
    const content = { ...recipe, tools: [tool], recipeIngredient: [{ food, referencedRecipe: nested }] };
    const exported = JSON.parse(await readFile(createRecipeFile(content, recipe.slug)));
    for (const projected of [exported, exported.recipeIngredient[0].referencedRecipe]) {
      expect(projected.tools).toEqual([{ id: "tool-id", name: "pot" }]);
      expect(projected.recipeIngredient[0].food).toEqual({ id: "food-id", name: "lentils" });
    }
    expect(JSON.stringify(exported)).not.toContain("PRIVATE");
  });

  it("uses a safe filename", () => {
    expect(createRecipeFile(recipe, "../../soup\n").name).toBe("..-..-soup-.json");
  });

  it("shares only the file synchronously before awaiting", async () => {
    const file = createRecipeFile(recipe, recipe.slug);
    const download = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
    const result = shareRecipeFile(file);
    expect(navigator.share).toHaveBeenCalledWith({ files: [file] });
    expect(await result).toBe("shared");
    expect(download).not.toHaveBeenCalled();
  });

  it.each(["http", "no-share", "no-can-share", "json-rejected", "can-share-throws"])("reports unavailable without downloading when %s", async (mode) => {
    if (mode === "http") vi.stubGlobal("isSecureContext", false);
    if (mode === "no-share") vi.stubGlobal("navigator", {});
    if (mode === "no-can-share") vi.stubGlobal("navigator", { share: vi.fn() });
    if (mode === "json-rejected") vi.mocked(navigator.canShare).mockReturnValue(false);
    if (mode === "can-share-throws") vi.mocked(navigator.canShare).mockImplementation(() => { throw new TypeError(); });
    const file = createRecipeFile(recipe, recipe.slug);
    const download = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
    expect(await shareRecipeFile(file)).toBe("unavailable");
    expect(download).not.toHaveBeenCalled();
  });

  it("never downloads on cancellation", async () => {
    vi.mocked(navigator.share).mockRejectedValue(new DOMException("Cancelled", "AbortError"));
    const download = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
    expect(await shareRecipeFile(createRecipeFile(recipe, recipe.slug))).toBe("cancelled");
    expect(download).not.toHaveBeenCalled();
  });

  it.each(["NotAllowedError", "TypeError", "DataError"])("reports unavailable after %s", async (name) => {
    vi.mocked(navigator.share).mockRejectedValue(new DOMException("Rejected", name));
    const download = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
    expect(await shareRecipeFile(createRecipeFile(recipe, recipe.slug))).toBe("unavailable");
    expect(download).not.toHaveBeenCalled();
  });

  it("cleans up the download element and eventually revokes its URL", () => {
    vi.useFakeTimers();
    const createObjectURL = vi.fn(() => "blob:recipe");
    const revokeObjectURL = vi.fn();
    vi.stubGlobal("URL", { createObjectURL, revokeObjectURL });
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
    const file = createRecipeFile(recipe, recipe.slug);
    downloadRecipeFile(file);
    expect(click).toHaveBeenCalledOnce();
    expect(createObjectURL).toHaveBeenCalledWith(file);
    expect(document.querySelector("a[download]")).toBeNull();
    expect(revokeObjectURL).not.toHaveBeenCalled();
    vi.runAllTimers();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:recipe");
  });
});
