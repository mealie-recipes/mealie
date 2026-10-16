// Keep Mealie's recipe field names and values, but not account details, comments,
// instance settings or arbitrary extras from the authenticated raw export.
const recipeFields = new Set([
  "id", "name", "slug", "description", "recipeServings", "recipeYieldQuantity", "recipeYield",
  "totalTime", "prepTime", "cookTime", "performTime", "recipeCategory", "tags", "tools",
  "totalTimeSeconds", "prepTimeSeconds", "performTimeSeconds",
  "orgURL", "recipeIngredient", "recipeInstructions", "nutrition", "notes",
]);
const privateFields = new Set([
  "groupId", "householdId", "userId", "extras", "householdsWithTool", "householdsWithIngredientFood",
]);

function withoutPrivateMetadata(value: unknown, isRecipe = false): unknown {
  if (Array.isArray(value)) return value.map(nested => withoutPrivateMetadata(nested, isRecipe));
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value)
      .filter(([key]) => !privateFields.has(key) && (!isRecipe || recipeFields.has(key)))
      .map(([key, nested]) => [key, withoutPrivateMetadata(nested, key === "referencedRecipe")]));
  }
  return value;
}

export function createRecipeFile(recipe: Record<string, unknown>, slug: string): File {
  const content = withoutPrivateMetadata(recipe, true);
  // eslint-disable-next-line no-control-regex -- Remove control characters from download filenames.
  const filename = (slug.replace(/[/\\\x00-\x1F\x7F]/g, "-") || "recipe") + ".json";
  return new File([JSON.stringify(content, null, 2)], filename, { type: "application/json" });
}

export function downloadRecipeFile(file: File): void {
  const url = URL.createObjectURL(file);
  const link = document.createElement("a");
  link.href = url;
  link.download = file.name;
  document.body.appendChild(link);
  link.click();
  link.remove();
  // Revoking immediately can race the browser's download navigation.
  setTimeout(() => URL.revokeObjectURL(url), 60_000);
}

/** Call directly from a user gesture, with an already prepared file. */
export async function shareRecipeFile(file: File): Promise<"shared" | "unavailable" | "cancelled"> {
  try {
    if (window.isSecureContext && typeof navigator.share === "function"
      && typeof navigator.canShare === "function" && navigator.canShare({ files: [file] })) {
      await navigator.share({ files: [file] });
      return "shared";
    }
  }
  catch (error) {
    // AbortError also covers platforms with no chosen share target. Never turn
    // dismissal into an unexpected download; an explicit download stays available.
    if (error && typeof error === "object" && "name" in error && error.name === "AbortError") return "cancelled";
  }
  return "unavailable";
}
