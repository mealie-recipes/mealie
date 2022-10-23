<template>
  <div>
    <v-form ref="domUrlForm" @submit.prevent="createByUrl(recipeUrl, importKeywordsAsTags, stayInEditMode)">
      <div>
        <v-card-title class="headline"> Scrape Recipe </v-card-title>
        <v-card-text>
          Scrape a recipe by url. Provide the url for the site you want to scrape, and Mealie will attempt to scrape the
          recipe from that site and add it to your collection.
          <v-text-field
            v-model="recipeUrl"
            :label="$t('new-recipe.recipe-url')"
            :prepend-inner-icon="$globals.icons.link"
            validate-on-blur
            autofocus
            filled
            clearable
            class="rounded-lg mt-2"
            rounded
            :rules="[validators.url]"
            :hint="$t('new-recipe.url-form-hint')"
            persistent-hint
          ></v-text-field>
          <v-checkbox v-model="importKeywordsAsTags" hide-details label="Import original keywords as tags" />
          <v-checkbox v-model="stayInEditMode" hide-details label="Stay in Edit mode" />
        </v-card-text>
        <v-card-actions class="justify-center">
          <div style="width: 250px">
            <BaseButton :disabled="recipeUrl === null" rounded block type="submit" :loading="loading" />
          </div>
        </v-card-actions>
      </div>
    </v-form>
    <v-expand-transition>
      <v-alert v-show="error" color="error" class="mt-6 white--text">
        <v-card-title class="ma-0 pa-0">
          <v-icon left color="white" x-large> {{ $globals.icons.robot }} </v-icon>
          {{ $t("new-recipe.error-title") }}
        </v-card-title>
        <v-divider class="my-3 mx-2"></v-divider>

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
          <a href="https://github.com/hay-kot/mealie/issues" target="_blank" rel="noreferrer nofollow">
            {{ $t("new-recipe.github-issues") }}
          </a>
          <a href="https://schema.org/Recipe" target="_blank" rel="noreferrer nofollow">
            {{ $t("new-recipe.recipe-markup-specification") }}
          </a>
        </div>
      </v-alert>
    </v-expand-transition>
  </div>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  ref,
  useRouter,
  computed,
  useRoute,
  onMounted,
} from "@nuxtjs/composition-api";
import { AxiosResponse } from "axios";
import { useUserApi } from "~/composables/api";
import { validators } from "~/composables/use-validators";
import { VForm } from "~/types/vuetify";

export default defineComponent({
  setup() {
    const state = reactive({
      error: false,
      loading: false,
    });

    const api = useUserApi();
    const route = useRoute();
    const router = useRouter();

    function handleResponse(response: AxiosResponse<string> | null, edit = false) {
      if (response?.status !== 201) {
        state.error = true;
        state.loading = false;
        return;
      }
      router.push(`/recipe/${response.data}?edit=${edit.toString()}`);
    }

    const recipeUrl = computed({
      set(recipe_import_url: string | null) {
        if (recipe_import_url !== null) {
          recipe_import_url = recipe_import_url.trim();
          router.replace({ query: { ...route.value.query, recipe_import_url } });
        }
      },
      get() {
        return route.value.query.recipe_import_url as string | null;
      },
    });

    const importKeywordsAsTags = computed({
      get() {
        return route.value.query.use_keywords === "1";
      },
      set(v: boolean) {
        router.replace({ query: { ...route.value.query, use_keywords: v ? "1" : "0" } });
      },
    });

    const stayInEditMode = computed({
      get() {
        return route.value.query.edit === "1";
      },
      set(v: boolean) {
        router.replace({ query: { ...route.value.query, edit: v ? "1" : "0" } });
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
      handleResponse(response, stayInEditMode);
    }

    return {
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
