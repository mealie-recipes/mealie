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
          <v-card-text class="pa-0">
            <p>{{ $t('recipe.scrape-recipe-description') }}</p>
            <p v-if="group?.aiProviderSettings?.audioProviderEnabled">
              {{ $t('recipe.scrape-recipe-description-transcription') }}
            </p>
          </v-card-text>
          <v-card-text class="px-0">
            <p>
              {{ $t('recipe.scrape-recipe-have-a-lot-of-recipes') }}
              <router-link :to="bulkImporterTarget" class="text-primary">{{ $t('recipe.scrape-recipe-suggest-bulk-importer') }}</router-link>.
            </p>
            <p>
              {{ $t('recipe.scrape-recipe-have-raw-html-or-json-data') }}
              <router-link :to="htmlOrJsonImporterTarget" class="text-primary">{{ $t('recipe.scrape-recipe-you-can-import-from-raw-data-directly') }}</router-link>.
            </p>
          </v-card-text>
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
              <!-- render &nbsp; to maintain layout -->
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
            class="dark text-primary"
            href="https://developers.google.com/search/docs/data-types/recipe"
            target="_blank"
            rel="noreferrer nofollow"
          >
            {{ $t("new-recipe.google-ld-json-info") }}
          </a>
          <a
            class="text-primary"
            href="https://github.com/mealie-recipes/mealie/issues"
            target="_blank"
            rel="noreferrer nofollow"
          >
            {{ $t("new-recipe.github-issues") }}
          </a>
          <a
            class="text-primary"
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

<script setup lang="ts">
import type { AxiosResponse } from "axios";
import { useUserApi } from "~/composables/api";
import { useGroupSelf } from "~/composables/use-groups";
import { useTagStore } from "~/composables/store/use-tag-store";
import { useNewRecipeOptions } from "~/composables/use-new-recipe-options";
import { validators } from "~/composables/use-validators";
import type { VForm } from "~/types/auto-forms";

definePageMeta({
  key: route => route.path,
});
const state = reactive({
  error: false,
  loading: false,
});

const auth = useMealieAuth();
const api = useUserApi();
const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");
const { group } = useGroupSelf();

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
    // Prefer the 'url' share field (recipe_import_url, populated by Chrome when
    // sharing a page URL). Fall back to the 'text' share field (recipe_import_text)
    // for apps that share URLs as plain text, but only when the text value is
    // actually a valid http/https URL — shared text can be arbitrary.
    const urlFromField = route.query.recipe_import_url as string | null;
    if (urlFromField) {
      return urlFromField;
    }
    const textFromField = route.query.recipe_import_text as string | null;
    if (textFromField) {
      try {
        const parsed = new URL(textFromField);
        if (parsed.protocol === "http:" || parsed.protocol === "https:") {
          return textFromField;
        }
      }
      catch { /* not a URL, ignore */ }
    }
    return null;
  },
});

onMounted(() => {
  if (recipeUrl.value) {
    // Apply legacy query params for older automations such as the Bookmarklet.
    // These are no longer used by the app itself but are easy to keep supporting.
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

    // The URL is pre-filled via the recipeUrl computed property.
    // Do not auto-submit: the user should review the import options and
    // confirm by clicking the submit button.
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

const createStatus = ref<string | null>(null);
async function createByUrl(url: string | null, importKeywordsAsTags: boolean, importCategories: boolean) {
  if (url === null) {
    return;
  }

  if (!domUrlForm.value?.validate() || url === "") {
    console.log("Invalid URL", url);
    return;
  }
  state.loading = true;
  const { response } = await api.recipes.createOneByUrl(
    url,
    importKeywordsAsTags,
    importCategories,
    (message: string) => createStatus.value = message,
  );
  createStatus.value = null;
  handleResponse(response, importKeywordsAsTags);
}
</script>

<style scoped>
.force-url-white a {
  color: white !important;
}
</style>
