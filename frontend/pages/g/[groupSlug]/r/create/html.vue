<template>
  <v-form
    ref="domUrlForm"
    @submit.prevent="createFromHtmlOrJson(newRecipeData, importKeywordsAsTags, importCategories, newRecipeUrl)"
  >
    <div>
      <v-card-title class="headline">
        {{ $t('recipe.import-from-html-or-json') }}
      </v-card-title>
      <v-card-text>
        <p>
          {{ $t("recipe.import-from-html-or-json-description") }}
        </p>
        <p>
          {{ $t("recipe.json-import-format-description-colon") }}
          <a
            href="https://schema.org/Recipe"
            target="_blank"
          >https://schema.org/Recipe</a>
        </p>
        <v-switch
          v-model="isEditJSON"
          :label="$t('recipe.json-editor')"
          color="primary"
          class="mt-2"
          @change="handleIsEditJson"
        />
        <v-text-field
          v-model="newRecipeUrl"
          :label="$t('new-recipe.recipe-url')"
          :prepend-inner-icon="$globals.icons.link"
          validate-on="blur"
          variant="solo-filled"
          clearable
          rounded
          :rules="[validators.urlOptional]"
          :hint="$t('new-recipe.copy-and-paste-the-source-url-of-your-data-optional')"
          persistent-hint
          class="mt-10 mb-4"
          style="max-width: 500px"
        />
        <RecipeJsonEditor
          v-if="isEditJSON"
          v-model="newRecipeData"
          height="250px"
          mode="code"
          :main-menu-bar="false"
        />
        <v-textarea
          v-else
          v-model="newRecipeData"
          :label="$t('new-recipe.recipe-html-or-json')"
          :prepend-inner-icon="$globals.icons.codeTags"
          validate-on="blur"
          autofocus
          variant="solo-filled"
          clearable
          rounded
        />
        <v-checkbox
          v-model="importKeywordsAsTags"
          color="primary"
          hide-details
          :label="$t('recipe.import-original-keywords-as-tags')"
        />
        <v-checkbox
          v-model="importCategories"
          color="primary"
          hide-details
          :label="$t('recipe.import-original-categories')"
        />
        <v-checkbox
          v-model="stayInEditMode"
          color="primary"
          hide-details
          :label="$t('recipe.stay-in-edit-mode')"
        />
        <v-checkbox
          v-model="parseRecipe"
          color="primary"
          hide-details
          :label="$t('recipe.parse-recipe-ingredients-after-import')"
        />
      </v-card-text>
      <v-card-actions class="justify-center">
        <div style="width: 250px">
          <BaseButton
            :disabled="!newRecipeData"
            rounded
            block
            type="submit"
            :loading="loading"
          />
        </div>
      </v-card-actions>
    </div>
  </v-form>
</template>

<script lang="ts">
import type { AxiosResponse } from "axios";
import { useTagStore } from "~/composables/store/use-tag-store";
import { useUserApi } from "~/composables/api";
import { useNewRecipeOptions } from "~/composables/use-new-recipe-options";
import { validators } from "~/composables/use-validators";
import type { VForm } from "~/types/auto-forms";

export default defineNuxtComponent({
  setup() {
    const state = reactive({
      error: false,
      loading: false,
      isEditJSON: false,
    });
    const $auth = useMealieAuth();
    const route = useRoute();
    const groupSlug = computed(() => route.params.groupSlug as string || $auth.user.value?.groupSlug || "");
    const domUrlForm = ref<VForm | null>(null);

    const api = useUserApi();
    const tags = useTagStore();

    const {
      importKeywordsAsTags,
      importCategories,
      stayInEditMode,
      parseRecipe,
      navigateToRecipe,
    } = useNewRecipeOptions();

    function handleResponse(response: AxiosResponse<string> | null, refreshTags = false) {
      if (response?.status !== 201) {
        state.error = true;
        state.loading = false;
        return;
      }
      if (refreshTags) {
        tags.actions.refresh();
      }

      navigateToRecipe(response.data, groupSlug.value, `/g/${groupSlug.value}/r/create/html`);
    }

    const newRecipeData = ref<string | object | null>(null);
    const newRecipeUrl = ref<string | null>(null);

    function handleIsEditJson() {
      if (state.isEditJSON) {
        if (newRecipeData.value) {
          try {
            newRecipeData.value = JSON.parse(newRecipeData.value as string);
          }
          catch {
            newRecipeData.value = { data: newRecipeData.value };
          }
        }
        else {
          newRecipeData.value = {};
        }
      }
      else if (newRecipeData.value && Object.keys(newRecipeData.value).length > 0) {
        newRecipeData.value = JSON.stringify(newRecipeData.value);
      }
      else {
        newRecipeData.value = null;
      }
    }
    handleIsEditJson();

    async function createFromHtmlOrJson(htmlOrJsonData: string | object | null, importKeywordsAsTags: boolean, importCategories: boolean, url: string | null = null) {
      if (!htmlOrJsonData) {
        return;
      }

      const isValid = await domUrlForm.value?.validate();
      if (!isValid?.valid) {
        return;
      }

      let dataString;
      if (typeof htmlOrJsonData === "string") {
        dataString = htmlOrJsonData;
      }
      else {
        dataString = JSON.stringify(htmlOrJsonData);
      }

      state.loading = true;
      const { response } = await api.recipes.createOneByHtmlOrJson(dataString, importKeywordsAsTags, importCategories, url);
      handleResponse(response, importKeywordsAsTags);
    }

    return {
      domUrlForm,
      importKeywordsAsTags,
      stayInEditMode,
      parseRecipe,
      importCategories,
      newRecipeData,
      newRecipeUrl,
      handleIsEditJson,
      createFromHtmlOrJson,
      ...toRefs(state),
      validators,
    };
  },
});
</script>
