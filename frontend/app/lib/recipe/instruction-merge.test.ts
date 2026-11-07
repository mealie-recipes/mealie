import { describe, expect, test } from "vitest";
import { mergeSteps, undoStepMerge } from "./instruction-merge";
import type { RecipeStep } from "~/lib/api/types/recipe";

function step(id: string, overrides: Partial<RecipeStep> = {}): RecipeStep {
  return {
    id,
    title: `Title ${id}`,
    text: `Text ${id}`,
    ingredientReferences: [],
    noteReferences: [],
    ...overrides,
  };
}

function refs(...ids: string[]) {
  return ids.map(referenceId => ({ referenceId }));
}

describe("mergeSteps", () => {
  test("appends the source text and removes the source step", () => {
    const steps = [step("a"), step("b"), step("c")];

    mergeSteps(steps, 0, 1);

    expect(steps.map(s => s.id)).toEqual(["a", "c"]);
    expect(steps[0]!.text).toBe("Text a Text b");
  });

  test("keeps linked ingredients and notes from both steps without duplicates", () => {
    const steps = [
      step("a", { ingredientReferences: refs("i1", "i2"), noteReferences: refs("n1") }),
      step("b", { ingredientReferences: refs("i2", "i3"), noteReferences: refs("n1", "n2") }),
    ];

    mergeSteps(steps, 0, 1);

    expect(steps[0]!.ingredientReferences).toEqual(refs("i1", "i2", "i3"));
    expect(steps[0]!.noteReferences).toEqual(refs("n1", "n2"));
  });

  test("handles steps with no reference arrays", () => {
    const steps = [
      step("a", { ingredientReferences: undefined, noteReferences: undefined }),
      step("b", { ingredientReferences: refs("i1"), noteReferences: undefined }),
    ];

    mergeSteps(steps, 0, 1);

    expect(steps[0]!.ingredientReferences).toEqual(refs("i1"));
    expect(steps[0]!.noteReferences).toEqual([]);
  });

  test("does nothing when there is no step above", () => {
    const steps = [step("a"), step("b")];

    expect(mergeSteps(steps, -1, 0)).toBeNull();
    expect(steps).toEqual([step("a"), step("b")]);
  });
});

describe("undoStepMerge", () => {
  test("restores both steps as they were before the merge", () => {
    const original = [
      step("a", { ingredientReferences: refs("i1"), noteReferences: refs("n1") }),
      step("b", { ingredientReferences: refs("i2"), noteReferences: refs("n2"), summary: "s", durationSeconds: 60 }),
    ];
    const steps = structuredClone(original);

    const merge = mergeSteps(steps, 0, 1)!;
    undoStepMerge(steps, merge);

    expect(steps).toEqual(original);
  });

  test("undoes several merges in reverse order", () => {
    const original = [
      step("a", { ingredientReferences: refs("i1") }),
      step("b", { ingredientReferences: refs("i2") }),
      step("c", { ingredientReferences: refs("i3") }),
      step("d"),
    ];
    const steps = structuredClone(original);

    const merges = [mergeSteps(steps, 1, 2)!, mergeSteps(steps, 0, 1)!];
    expect(steps.map(s => s.id)).toEqual(["a", "d"]);
    expect(steps[0]!.ingredientReferences).toEqual(refs("i1", "i2", "i3"));

    for (const merge of merges.reverse()) {
      undoStepMerge(steps, merge);
    }

    expect(steps).toEqual(original);
  });
});
