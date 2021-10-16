<template>
  <v-container class="narrow-container flex-column">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="175" max-width="175" :src="require('~/static/svgs/recipes-create.svg')"></v-img>
      </template>
      <template #title> Recipe Creation </template>
      Select one of the various ways to create a recipe
    </BasePageTitle>
    <BaseOverflowButton v-model="tab" rounded class="mx-2" outlined :items="tabs"> </BaseOverflowButton>
  
    <section>
      <v-tabs-items v-model="tab" class="mt-10">
        <v-tab-item value="url" eager>
          <v-form ref="domUrlForm" @submit.prevent="createByUrl(recipeUrl)">
            <v-card outlined>
              <v-card-text>
                <v-text-field
                  v-model="recipeUrl"
                  :label="$t('new-recipe.recipe-url')"
                  validate-on-blur
                  autofocus
                  class="rounded-lg my-auto"
                  :rules="[validators.url]"
                  :hint="$t('new-recipe.url-form-hint')"
                  persistent-hint
                ></v-text-field>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <BaseButton type="submit" :loading="loading" />
              </v-card-actions>
            </v-card>
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
              <div class="d-flex justify-end">
                <v-btn
                  dark
                  outlined
                  :to="{ path: '/recipes/debugger', query: { test_url: recipeUrl } }"
                  @click="addRecipe = false"
                >
                  <v-icon left> {{ $globals.icons.externalLink }} </v-icon>
                  {{ $t("new-recipe.view-scraped-data") }}
                </v-btn>
              </div>
            </v-alert>
          </v-expand-transition>
        </v-tab-item>
        <v-tab-item value="new" eager>
          <v-card outlined>
            <v-card-text>
              <v-form ref="domCreateByName">
                <v-text-field
                  v-model="newRecipeName"
                  :label="$t('recipe.recipe-name')"
                  validate-on-blur
                  autofocus
                  class="rounded-lg my-auto"
                  :rules="[validators.required]"
                  hint="New recipe names must be unique"
                  persistent-hint
                ></v-text-field>
              </v-form>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <BaseButton :loading="loading" @click="createByName(newRecipeName)" />
            </v-card-actions>
          </v-card>
        </v-tab-item>
        <v-tab-item value="zip" eager>
          <v-form>
            <v-card outlined>
              <v-card-text>
                <v-file-input
                  v-model="newRecipeZip"
                  accept=".zip"
                  placeholder="Select your files"
                  label="File input"
                  truncate-length="100"
                  hint=".zip files must have been exported from Mealie"
                  persistent-hint
                  :prepend-icon="$globals.icons.zip"
                >
                </v-file-input>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <BaseButton :loading="loading" @click="createByZip" />
              </v-card-actions>
            </v-card>
          </v-form>
        </v-tab-item>
      </v-tabs-items>
    </section>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, ref, useRouter, useContext } from "@nuxtjs/composition-api";
import { useApiSingleton } from "~/composables/use-api";
import { validators } from "~/composables/use-validators";
export default defineComponent({
  setup() {
    const state = reactive({
      error: false,
      loading: false,
    });

    // @ts-ignore - $globals not found in type definition
    const { $globals } = useContext();

    const tabs = [
      {
        icon: $globals.icons.edit,
        text: "Create Recipe",
        value: "new",
      },
      {
        icon: $globals.icons.link,
        text: "Import with URL",
        value: "url",
      },
      {
        icon: $globals.icons.zip,
        text: "Import with .zip",
        value: "zip",
      },
    ];

    const api = useApiSingleton();
    const router = useRouter();

    function handleResponse(response: any) {
      if (response?.status !== 201) {
        state.error = true;
        state.loading = false;
        return;
      }
      console.log(response);
      router.push(`/recipe/${response.data}`);
    }

    // ===================================================
    // Recipe URL Import
    // @ts-ignore
    const domUrlForm = ref<VForm>(null);

    async function createByUrl(url: string) {
      if (!domUrlForm.value.validate() || url === "") {
        return;
      }
      state.loading = true;
      const { response } = await api.recipes.createOneByUrl(url);
      if (response?.status !== 201) {
        state.error = true;
        state.loading = false;
        return;
      }
      handleResponse(response);
    }

    // ===================================================
    // Recipe Create By Name
    const newRecipeName = ref("");
    // @ts-ignore
    const domCreateByName = ref<VForm>(null);

    async function createByName(name: string) {
      if (!domCreateByName.value.validate() || name === "") {
        return;
      }
      const { response } = await api.recipes.createOne({ name });
      console.log("Create By Name Func", response);
      handleResponse(response);
    }

    // ===================================================
    // Recipe Import From Zip File
    // @ts-ignore
    const newRecipeZip = ref<File>(null);
    const newRecipeZipFileName = "archive";

    async function createByZip() {
      if (!newRecipeZip.value) {
        return;
      }
      const formData = new FormData();
      formData.append(newRecipeZipFileName, newRecipeZip.value);

      const { response } = await api.upload.file("/api/recipes/create-from-zip", formData);
      console.log(response);
      handleResponse(response);
    }

    return {
      tabs,
      domCreateByName,
      domUrlForm,
      newRecipeName,
      newRecipeZip,
      createByName,
      createByUrl,
      createByZip,
      ...toRefs(state),
      validators,
    };
  },
  head() {
    return {
      title: this.$t("general.create") as string,
    };
  },
  // Computed State is used because of the limitation of vue-composition-api in v2.0
  computed: {
    tab: {
      set(tab) {
        this.$router.replace({ query: { ...this.$route.query, tab } });
      },
      get() {
        return this.$route.query.tab;
      },
    },
    recipeUrl: {
      set(recipe_import_url) {
        this.$router.replace({ query: { ...this.$route.query, recipe_import_url } });
      },
      get() {
        return this.$route.query.recipe_import_url;
      },
    },
  },
});
</script>


<style>
.force-white > a {
  color: white !important;
}
</style>
