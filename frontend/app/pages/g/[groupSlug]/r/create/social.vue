<template>
  <div>
    <v-form
      ref="domUrlForm"
      @submit.prevent="createBySocialUrl(recipeUrl, importKeywordsAsTags, importCategories)"
    >
      <div>
        <v-card-title class="headline">
          {{ $t('recipe.scrape-social-recipe') }}
        </v-card-title>
        <v-card-text>
          <p>{{ $t('recipe.scrape-social-recipe-description') }}</p>
          <v-text-field
            v-model="recipeUrl"
            :label="$t('new-recipe.recipe-url')"
            :prepend-inner-icon="$globals.icons.link"
            validate-on="blur"
            autofocus
            variant="solo-filled"
            clearable
            class="rounded-lg mt-2"
            rounded
            :rules="[validators.url]"
            :hint="$t('new-recipe.url-form-hint')"
            persistent-hint
          />
        </v-card-text>
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
        <v-card-actions class="justify-center">
          <div style="width: 100%" class="text-center">
            <div style="width: 250px; margin: 0 auto">
              <BaseButton
                :disabled="recipeUrl === null"
                rounded
                block
                type="submit"
                :loading="state.loading"
              />
            </div>
            <v-card-text class="py-2">
              {{ createStatus }}&nbsp;
            </v-card-text>
          </div>
        </v-card-actions>
      </div>
    </v-form>
    <v-expand-transition>
      <v-alert
        v-if="state.error"
        color="error"
        class="mt-6 white--text"
      >
        <v-card-title class="ma-0 pa-0">
          <v-icon
            start
            color="white"
            size="x-large"
          >
            {{ $globals.icons.robot }}
          </v-icon>
          {{ $t("new-recipe.error-title") }}
        </v-card-title>
        <v-divider class="my-3 mx-2" />
        <p>{{ state.errorMessage || $t("new-recipe.error-details") }}</p>
      </v-alert>
    </v-expand-transition>
  </div>
</template>

<script setup lang="ts">
import type { AxiosResponse } from "axios";
import { useUserApi } from "~/composables/api";
import { useTagStore } from "~/composables/store/use-tag-store";
import { useNewRecipeOptions } from "~/composables/use-new-recipe-options";
import { validators } from "~/composables/use-validators";
import type { VForm } from "~/types/auto-forms";

definePageMeta({
  key: route => route.path,
});

const state = reactive({
  error: false,
  errorMessage: "",
  loading: false,
});

const auth = useMealieAuth();
const api = useUserApi();
const route = useRoute();
const router = useRouter();
const tags = useTagStore();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");

const {
  importKeywordsAsTags,
  importCategories,
  stayInEditMode,
  parseRecipe,
  navigateToRecipe,
} = useNewRecipeOptions();

function extractUrl(value: string | null | undefined) {
  if (!value) {
    return null;
  }
  const match = value.match(/https?:\/\/[^\s]+/);
  return match?.[0] ?? null;
}

function handleResponse(response: AxiosResponse<string> | null, error: Error | null, refreshTags = false) {
  if (response?.status !== 201) {
    state.error = true;
    state.errorMessage = error?.message ?? "";
    state.loading = false;
    return;
  }
  if (refreshTags) {
    tags.actions.refresh();
  }

  navigateToRecipe(response.data, groupSlug.value, `/g/${groupSlug.value}/r/create/social`);
}

const recipeUrl = computed({
  set(recipe_import_url: string | null) {
    if (recipe_import_url !== null) {
      recipe_import_url = recipe_import_url.trim();
      router.replace({ query: { ...route.query, recipe_import_url } });
    }
  },
  get() {
    return (
      extractUrl(route.query.recipe_import_url as string | null)
      ?? extractUrl(route.query.recipe_import_text as string | null)
      ?? null
    );
  },
});

const domUrlForm = ref<VForm | null>(null);

const isLeaving = ref(false);
onBeforeRouteLeave((to) => {
  if (isLeaving.value) {
    return;
  }
  isLeaving.value = true;
  router.replace({ query: undefined }).then(() => router.push(to));
});

const createStatus = ref<string | null>(null);
async function createBySocialUrl(url: string | null, includeTags: boolean, includeCategories: boolean) {
  if (url === null) {
    return;
  }

  if (!domUrlForm.value?.validate() || url === "") {
    return;
  }

  state.loading = true;
  state.error = false;
  state.errorMessage = "";

  const { response, error } = await api.recipes.createOneBySocialUrl(
    url,
    includeTags,
    includeCategories,
    (message: string) => createStatus.value = message,
  );
  createStatus.value = null;
  handleResponse(response, error, includeTags);
}
</script>
