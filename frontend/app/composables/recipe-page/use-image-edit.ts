import { inject } from "vue";
import type { InjectionKey, Ref } from "vue";
import type { AxiosRequestConfig } from "axios";
import type { RequestResponse } from "~/lib/api/types/non-generated";
import type { Recipe } from "~/lib/api/types/recipe";

export type ImageEdit = <T>(request: (config?: AxiosRequestConfig) => Promise<RequestResponse<T>>) => Promise<RequestResponse<T> | undefined>;
export const imageEditKey: InjectionKey<ImageEdit> = Symbol("recipe-image-edit");

export function createImageEdit({ recipe, originalRecipe, saving, saveConflict }: {
  recipe: Ref<Recipe>;
  originalRecipe: Ref<Recipe | null>;
  saving: Ref<boolean>;
  saveConflict: Ref<boolean>;
}): ImageEdit {
  return async (request) => {
    if (saving.value) return;
    saving.value = true;
    saveConflict.value = false;
    try {
      const result = await request({
        headers: { "X-Recipe-Updated-At": originalRecipe.value?.updatedAt },
        suppressErrorAlertStatuses: [409],
      });
      if (result.error) {
        saveConflict.value = result.error.response?.status === 409;
      }
      else {
        const timestamp = result.response?.headers["x-recipe-updated-at"];
        if (typeof timestamp === "string" && originalRecipe.value) {
          originalRecipe.value.updatedAt = timestamp;
          recipe.value.updatedAt = timestamp;
        }
      }
      return result;
    }
    finally {
      saving.value = false;
    }
  };
}

export function useImageEdit(): ImageEdit {
  return inject(imageEditKey, request => request());
}
