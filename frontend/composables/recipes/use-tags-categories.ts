import { Ref, ref, useAsync } from "@nuxtjs/composition-api";
import { useUserApi } from "../api";
import { useAsyncKey } from "../use-utils";
import { CategoriesAPI } from "~/api/class-interfaces/organizer-categories";
import { TagsAPI } from "~/api/class-interfaces/organizer-tags";
import { RecipeTag, RecipeCategory } from "~/types/api-types/recipe";

export const allCategories = ref<RecipeCategory[] | null>([]);
export const allTags = ref<RecipeTag[] | null>([]);

function baseTagsCategories(
  reference: Ref<RecipeCategory[] | null> | Ref<RecipeTag[] | null>,
  api: TagsAPI | CategoriesAPI
) {
  function useAsyncGetAll() {
    useAsync(async () => {
      await refreshItems();
    }, useAsyncKey());
  }

  async function refreshItems() {
    const { data } = await api.getAll();
    reference.value = data;
  }

  async function createOne(payload: { name: string }) {
    const { data } = await api.createOne(payload);
    if (data) {
      refreshItems();
    }
  }

  async function deleteOne(slug: string) {
    const { data } = await api.deleteOne(slug);
    if (data) {
      refreshItems();
    }
  }

  async function updateOne(slug: string, payload: { name: string }) {
    // @ts-ignore // TODO: Fix Typescript Issue - Unsure how to fix this while also keeping mixins
    const { data } = await api.updateOne(slug, payload);
    if (data) {
      refreshItems();
    }
  }

  return { useAsyncGetAll, refreshItems, createOne, deleteOne, updateOne };
}

export const useTags = function () {
  const api = useUserApi();
  return {
    allTags,
    ...baseTagsCategories(allTags, api.tags),
  };
};
export const useCategories = function () {
  const api = useUserApi();
  return {
    allCategories,
    ...baseTagsCategories(allCategories, api.categories),
  };
};
