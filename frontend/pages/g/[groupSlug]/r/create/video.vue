<template>
  <div>
    <v-form
      ref="domUrlForm"
      @submit.prevent="createByVideoUrl(recipeUrl, importKeywordsAsTags)"
    >
      <div>
        <v-card-title class="headline">
          {{ $t('recipe.create-recipe-from-video') }}
        </v-card-title>
        <v-card-text>
          <p>{{ $t('recipe.create-recipe-from-video-description') }}</p>
          <v-text-field
            v-model="recipeUrl"
            :label="$t('recipe.recipe-from-video-url')"
            :prepend-inner-icon="$globals.icons.link"
            validate-on="blur"
            autofocus
            variant="solo-filled"
            clearable
            class="rounded-lg mt-2"
            rounded
            :rules="[validators.url]"
            :hint="$t('recipe.create-recipe-from-video-url-hint')"
            persistent-hint
          />
        </v-card-text>
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
            <p
              v-if="loading"
              class="text-center mt-2 text-caption"
            >
              {{ $t('recipe.create-recipe-from-video-loading-hint') }}
            </p>
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
            {{ $t('recipe.create-recipe-from-video-error-description') }}
          </p>
        </div>
        <div class="d-flex row justify-space-around my-3 force-url-white">
          <a
            class="dark"
            href="https://ytdl-org.github.io/youtube-dl/supportedsites.html"
            target="_blank"
            rel="noreferrer nofollow"
          >
            {{ $t('recipe.create-recipe-from-video-supported-sites') }}
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

      navigateToRecipe(response.data, groupSlug.value, `/g/${groupSlug.value}/r/create/video`);
    }

    const recipeUrl = computed({
      set(recipe_import_video_url: string | null) {
        if (recipe_import_video_url !== null) {
          recipe_import_video_url = recipe_import_video_url.trim();
          router.replace({ query: { ...route.query, recipe_import_video_url } });
        }
      },
      get() {
        return route.query.recipe_import_video_url as string | null;
      },
    });

    onMounted(() => {
      if (recipeUrl.value && recipeUrl.value.includes("https")) {
        // Check if we have a query params for using keywords as tags or staying in edit mode.
        // We don't use these in the app anymore, but older automations such as Bookmarklet might still use them,
        // and they're easy enough to support.

        const stayInEditModeParam = route.query.edit;
        if (stayInEditModeParam === "1") {
          stayInEditMode.value = true;
        }
        else if (stayInEditModeParam === "0") {
          stayInEditMode.value = false;
        }

        createByVideoUrl(recipeUrl.value, importKeywordsAsTags.value);
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

    async function createByVideoUrl(url: string | null, importKeywordsAsTags: boolean) {
      if (url === null) {
        return;
      }

      if (!domUrlForm.value?.validate() || url === "") {
        console.log("Invalid URL", url);
        return;
      }
      state.loading = true;
      const { response } = await api.recipes.createOneByVideoUrl(url, importKeywordsAsTags);
      handleResponse(response, importKeywordsAsTags);
    }

    return {
      bulkImporterTarget,
      htmlOrJsonImporterTarget,
      recipeUrl,
      importKeywordsAsTags,
      stayInEditMode,
      parseRecipe,
      domUrlForm,
      createByVideoUrl,
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
