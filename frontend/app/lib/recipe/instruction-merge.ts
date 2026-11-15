import type { RecipeStep } from "~/lib/api/types/recipe";

export interface StepMerge {
  target: number;
  source: number;
  targetStep: Pick<RecipeStep, "text" | "ingredientReferences" | "noteReferences">;
  sourceStep: RecipeStep;
}

function mergeReferences<T extends { referenceId?: string | null }>(target: T[] = [], source: T[] = []): T[] {
  const targetIds = new Set(target.map(ref => ref.referenceId));
  return [...target, ...source.filter(ref => !targetIds.has(ref.referenceId))];
}

/**
 * Merges `steps[source]` into `steps[target]` in place and removes the source step.
 * Returns the record `undoStepMerge` needs, or null when either index is out of range.
 */
export function mergeSteps(steps: RecipeStep[], target: number, source: number): StepMerge | null {
  const targetStep = steps[target];
  const sourceStep = steps[source];
  if (!targetStep || !sourceStep) {
    return null;
  }

  const merge: StepMerge = {
    target,
    source,
    targetStep: {
      text: targetStep.text,
      ingredientReferences: targetStep.ingredientReferences,
      noteReferences: targetStep.noteReferences,
    },
    sourceStep,
  };

  targetStep.text += " " + sourceStep.text;
  targetStep.ingredientReferences = mergeReferences(targetStep.ingredientReferences, sourceStep.ingredientReferences);
  targetStep.noteReferences = mergeReferences(targetStep.noteReferences, sourceStep.noteReferences);
  steps.splice(source, 1);

  return merge;
}

/**
 * Reverts a merge in place. Merges must be undone in reverse order, since the
 * stored indexes refer to the list as it was when that merge happened.
 */
export function undoStepMerge(steps: RecipeStep[], merge: StepMerge): void {
  const targetStep = steps[merge.target];
  if (!targetStep) {
    return;
  }

  Object.assign(targetStep, merge.targetStep);
  steps.splice(merge.source, 0, merge.sourceStep);
}
