<template>
  <div>
    <v-form
      ref="domUrlForm"
      @submit.prevent="createByUrl(recipeUrl, importKeywordsAsTags, importCategories)"
    >
      <div>
        <v-card-title class="headline">
          {{ $t('recipe.scrape-recipe') }}
        </v-card-title>
        <v-card-text>
          <p>{{ $t('recipe.scrape-recipe-description') }}</p>
          <p>
            {{ $t('recipe.scrape-recipe-have-a-lot-of-recipes') }}
            <router-link :to="bulkImporterTarget">{{ $t('recipe.scrape-recipe-suggest-bulk-importer') }}</router-link>.
            <br>
            {{ $t('recipe.scrape-recipe-have-raw-html-or-json-data') }}
            <router-link :to="htmlOrJsonImporterTarget">{{ $t('recipe.scrape-recipe-you-can-import-from-raw-data-directly') }}</router-link>.
          </p>
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
          <div style="width: 250px">
            <BaseButton
              :disabled="recipeUrl === null"
              rounded
              block
              type="submit"
              :loading="loading"
            />
          </div>
        </v-card-actions>
      </div>
    </v-form>
    <v-expand-transition>
      <v-alert
        v-if="error"
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

        <div class="force-url-white">
          <p>
            {{ $t("recipe.scrape-recipe-website-being-blocked") }}
            <router-link :to="htmlOrJsonImporterTarget">{{ $t("recipe.scrape-recipe-try-importing-raw-html-instead") }}</router-link>
          </p>
          <br>
          <p>
            {{ $t("new-recipe.error-details") }}
          </p>
        </div>
        <div class="d-flex row justify-space-around my-3 force-url-white">
          <a
            class="dark"
            href="https://developers.google.com/search/docs/data-types/recipe"
            target="_blank"
            rel="noreferrer nofollow"
          >
            {{ $t("new-recipe.google-ld-json-info") }}
          </a>
          <a
            href="https://github.com/mealie-recipes/mealie/issues"
            target="_blank"
            rel="noreferrer nofollow"
          >
            {{ $t("new-recipe.github-issues") }}
          </a>
          <a
            href="https://schema.org/Recipe"
            target="_blank"
            rel="noreferrer nofollow"
          >
            {{ $t("new-recipe.recipe-markup-specification") }}
          </a>
        </div>
      </v-alert>
    </v-expand-transition>
  </div>
</template>

<script lang="ts">
import type { AxiosResponse } from "axios";
import { useUserApi } from "~/composables/api";
import { useTagStore } from "~/composables/store/use-tag-store";
import { useNewRecipeOptions } from "~/composables/use-new-recipe-options";
import { validators } from "~/composables/use-validators";
import type { VForm } from "~/types/auto-forms";

export default defineNuxtComponent({
  setup() {
    definePageMeta({
      key: route => route.path,
    });
    const state = reactive({
      error: false,
      loading: false,
    });

    const $auth = useMealieAuth();
    const api = useUserApi();
    const route = useRoute();
    const groupSlug = computed(() => route.params.groupSlug as string || $auth.user.value?.groupSlug || "");

    const router = useRouter();
    const tags = useTagStore();

    const {
      importKeywordsAsTags,
      importCategories,
      stayInEditMode,
      parseRecipe,
      navigateToRecipe,
    } = useNewRecipeOptions();

    const bulkImporterTarget = computed(() => `/g/${groupSlug.value}/r/create/bulk`);
    const htmlOrJsonImporterTarget = computed(() => `/g/${groupSlug.value}/r/create/html`);

    function handleResponse(response: AxiosResponse<string> | null, refreshTags = false) {
      if (response?.status !== 201) {
        state.error = true;
        state.loading = false;
        return;
      }
      if (refreshTags) {
        tags.actions.refresh();
      }

      navigateToRecipe(response.data, groupSlug.value, `/g/${groupSlug.value}/r/create/url`);
    }

    const recipeUrl = computed({
      set(recipe_import_url: string | null) {
        if (recipe_import_url !== null) {
          recipe_import_url = recipe_import_url.trim();
          router.replace({ query: { ...route.query, recipe_import_url } });
        }
      },
      get() {
        return route.query.recipe_import_url as string | null;
      },
    });

    onMounted(() => {
      if (recipeUrl.value && recipeUrl.value.includes("https")) {
        // Check if we have a query params for using keywords as tags or staying in edit mode.
        // We don't use these in the app anymore, but older automations such as Bookmarklet might still use them,
        // and they're easy enough to support.
        const importKeywordsAsTagsParam = route.query.use_keywords;
        if (importKeywordsAsTagsParam === "1") {
          importKeywordsAsTags.value = true;
        }
        else if (importKeywordsAsTagsParam === "0") {
          importKeywordsAsTags.value = false;
        }

        const stayInEditModeParam = route.query.edit;
        if (stayInEditModeParam === "1") {
          stayInEditMode.value = true;
        }
        else if (stayInEditModeParam === "0") {
          stayInEditMode.value = false;
        }

        createByUrl(recipeUrl.value, importKeywordsAsTags.value);
        return;
      }
    });

    const domUrlForm = ref<VForm | null>(null);

    // Remove import URL from query params when leaving the page
    const isLeaving = ref(false);
    onBeforeRouteLeave((to) => {
      if (isLeaving.value) {
        return;
      }
      isLeaving.value = true;
      router.replace({ query: undefined }).then(() => router.push(to));
    });

    async function createByUrl(url: string | null, importKeywordsAsTags: boolean, importCategories: boolean) {
      if (url === null) {
        return;
      }

      if (!domUrlForm.value?.validate() || url === "") {
        console.log("Invalid URL", url);
        return;
      }
      state.loading = true;
      const { response } = await api.recipes.createOneByUrl(url, importKeywordsAsTags, importCategories);
      handleResponse(response, importKeywordsAsTags);
    }

    return {
      bulkImporterTarget,
      htmlOrJsonImporterTarget,
      recipeUrl,
      importKeywordsAsTags,
      importCategories: importCategories,
      stayInEditMode,
      parseRecipe,
      domUrlForm,
      createByUrl,
      ...toRefs(state),
      validators,
    };
  },
});
</script>

<style scoped>
.force-url-white a {
  color: white !important;
}
</style>
