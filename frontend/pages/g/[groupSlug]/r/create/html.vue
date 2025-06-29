<template>
  <v-form
    ref="domUrlForm"
    @submit.prevent="createFromHtmlOrJson(newRecipeData, importKeywordsAsTags, stayInEditMode)"
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
          class="mt-2"
          @change="handleIsEditJson"
        />
        <RecipeJsonEditor
          v-if="isEditJSON"
          v-model="newRecipeData"
          height="250px"
          class="mt-10"
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
          class="rounded-lg mt-2"
          rounded
          :hint="$t('new-recipe.url-form-hint')"
          persistent-hint
        />
        <v-checkbox
          v-model="importKeywordsAsTags"
          hide-details
          :label="$t('recipe.import-original-keywords-as-tags')"
        />
        <v-checkbox
          v-model="stayInEditMode"
          hide-details
          :label="$t('recipe.stay-in-edit-mode')"
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
    const router = useRouter();
    const tags = useTagStore();

    const importKeywordsAsTags = computed({
      get() {
        return route.query.use_keywords === "1";
      },
      set(v: boolean) {
        router.replace({ query: { ...route.query, use_keywords: v ? "1" : "0" } });
      },
    });

    const stayInEditMode = computed({
      get() {
        return route.query.edit === "1";
      },
      set(v: boolean) {
        router.replace({ query: { ...route.query, edit: v ? "1" : "0" } });
      },
    });

    function handleResponse(response: AxiosResponse<string> | null, edit = false, refreshTags = false) {
      if (response?.status !== 201) {
        state.error = true;
        state.loading = false;
        return;
      }
      if (refreshTags) {
        tags.actions.refresh();
      }

      router.push(`/g/${groupSlug.value}/r/${response.data}?edit=${edit.toString()}`);
    }

    const newRecipeData = ref<string | object | null>(null);

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

    async function createFromHtmlOrJson(htmlOrJsonData: string | object | null, importKeywordsAsTags: boolean, stayInEditMode: boolean) {
      if (!htmlOrJsonData || !domUrlForm.value?.validate()) {
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
      const { response } = await api.recipes.createOneByHtmlOrJson(dataString, importKeywordsAsTags);
      handleResponse(response, stayInEditMode, importKeywordsAsTags);
    }

    return {
      domUrlForm,
      importKeywordsAsTags,
      stayInEditMode,
      newRecipeData,
      handleIsEditJson,
      createFromHtmlOrJson,
      ...toRefs(state),
      validators,
    };
  },
});
</script>
