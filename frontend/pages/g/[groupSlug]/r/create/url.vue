<template>
  <div>
    <v-form
      ref="domUrlForm"
      @submit.prevent="createByUrl(recipeUrl, importKeywordsAsTags, stayInEditMode)"
    >
      <div>
        <v-card-title class="headline">
          {{ $t('recipe.scrape-recipe') }}
        </v-card-title>
        <v-card-text>
          <p>{{ $t('recipe.scrape-recipe-description') }}</p>
          <p>
            {{ $t('recipe.scrape-recipe-have-a-lot-of-recipes') }}
            <a :href="bulkImporterTarget">{{ $t('recipe.scrape-recipe-suggest-bulk-importer') }}</a>.
            <br>
            {{ $t('recipe.scrape-recipe-have-raw-html-or-json-data') }}
            <a :href="htmlOrJsonImporterTarget">{{ $t('recipe.scrape-recipe-you-can-import-from-raw-data-directly') }}</a>.
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
          v-model="stayInEditMode"
          color="primary"
          hide-details
          :label="$t('recipe.stay-in-edit-mode')"
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

        <p>
          {{ $t("new-recipe.error-details") }}
        </p>
        <div class="d-flex row justify-space-around my-3 force-white">
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

    const bulkImporterTarget = computed(() => `/g/${groupSlug.value}/r/create/bulk`);
    const htmlOrJsonImporterTarget = computed(() => `/g/${groupSlug.value}/r/create/html`);

    function handleResponse(response: AxiosResponse<string> | null, edit = false, refreshTags = false) {
      if (response?.status !== 201) {
        state.error = true;
        state.loading = false;
        return;
      }
      if (refreshTags) {
        tags.actions.refresh();
      }

      // we clear the query params first so if the user hits back, they don't re-import the recipe
      router.replace({ query: {} }).then(
        () => router.push(`/g/${groupSlug.value}/r/${response.data}?edit=${edit.toString()}`),
      );
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

    onMounted(() => {
      if (!recipeUrl.value) {
        return;
      }

      if (recipeUrl.value.includes("https")) {
        createByUrl(recipeUrl.value, importKeywordsAsTags.value, stayInEditMode.value);
      }
    });

    const domUrlForm = ref<VForm | null>(null);

    async function createByUrl(url: string | null, importKeywordsAsTags: boolean, stayInEditMode: boolean) {
      if (url === null) {
        return;
      }

      if (!domUrlForm.value?.validate() || url === "") {
        console.log("Invalid URL", url);
        return;
      }
      state.loading = true;
      const { response } = await api.recipes.createOneByUrl(url, importKeywordsAsTags);
      handleResponse(response, stayInEditMode, importKeywordsAsTags);
    }

    return {
      bulkImporterTarget,
      htmlOrJsonImporterTarget,
      recipeUrl,
      importKeywordsAsTags,
      stayInEditMode,
      domUrlForm,
      createByUrl,
      ...toRefs(state),
      validators,
    };
  },
});
</script>

<style>
.force-white > a {
  color: white !important;
}
</style>
