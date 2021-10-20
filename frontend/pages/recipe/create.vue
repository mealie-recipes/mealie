<template>
  <div>
    <v-container class="narrow-container flex-column pa-0">
      <BasePageTitle divider>
        <template #header>
          <v-img max-height="175" max-width="175" :src="require('~/static/svgs/recipes-create.svg')"></v-img>
        </template>
        <template #title> Recipe Creation </template>
        Select one of the various ways to create a recipe
        <template #content>
          <div class="ml-auto">
            <BaseOverflowButton v-model="tab" rounded outlined :items="tabs"> </BaseOverflowButton>
          </div>
        </template>
      </BasePageTitle>

      <section>
        <v-tabs-items v-model="tab" class="mt-2">
          <!-- Create From URL -->
          <v-tab-item value="url" eager>
            <v-form ref="domUrlForm" @submit.prevent="createByUrl(recipeUrl)">
              <v-card flat>
                <v-card-title class="headline"> Scrape Recipe </v-card-title>
                <v-card-text>
                  Scrape a recipe by url. Provide the url for the site you want to scrape, and Mealie will attempt to
                  scrape the recipe from that site and add it to your collection.
                  <v-text-field
                    v-model="recipeUrl"
                    :label="$t('new-recipe.recipe-url')"
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
                </v-card-text>
                <v-card-actions class="justify-center">
                  <div style="width: 250px">
                    <BaseButton rounded block type="submit" :loading="loading" />
                  </div>
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
              </v-alert>
            </v-expand-transition>
          </v-tab-item>

          <!-- Create By Name -->
          <v-tab-item value="new" eager>
            <v-card flat>
              <v-card-title class="headline"> Create Recipe </v-card-title>
              <v-card-text>
                Create a recipe by providing the name. All recipes must have unique names.
                <v-form ref="domCreateByName">
                  <v-text-field
                    v-model="newRecipeName"
                    :label="$t('recipe.recipe-name')"
                    validate-on-blur
                    autofocus
                    filled
                    clearable
                    class="rounded-lg mt-2"
                    rounded
                    :rules="[validators.required]"
                    hint="New recipe names must be unique"
                    persistent-hint
                  ></v-text-field>
                </v-form>
              </v-card-text>
              <v-card-actions class="justify-center">
                <div style="width: 250px">
                  <BaseButton rounded block :loading="loading" @click="createByName(newRecipeName)" />
                </div>
              </v-card-actions>
            </v-card>
          </v-tab-item>

          <!-- Create By Zip -->
          <v-tab-item value="zip" eager>
            <v-form>
              <v-card>
                <v-card-title class="headline"> Import from Zip </v-card-title>
                <v-card-text>
                  Import a single recipe that was exported from another Mealie instance.
                  <v-file-input
                    v-model="newRecipeZip"
                    accept=".zip"
                    label=".zip"
                    filled
                    clearable
                    class="rounded-lg mt-2"
                    rounded
                    truncate-length="100"
                    hint=".zip files must have been exported from Mealie"
                    persistent-hint
                    prepend-icon=""
                    :prepend-inner-icon="$globals.icons.zip"
                  >
                  </v-file-input>
                </v-card-text>
                <v-card-actions class="justify-center">
                  <div style="width: 250px">
                    <BaseButton large rounded block :loading="loading" @click="createByZip" />
                  </div>
                </v-card-actions>
              </v-card>
            </v-form>
          </v-tab-item>

          <!-- Create By Zip -->
          <v-tab-item value="debug" eager>
            <v-form ref="domUrlForm" @submit.prevent="debugUrl(recipeUrl)">
              <v-card flat>
                <v-card-title class="headline"> Recipe Debugger</v-card-title>
                <v-card-text>
                  Grab the URL of the recipe you want to debug and paste it here. The URL will be scraped by the recipe
                  scraper and the results will be displayed. If you don't see any data returned, the site you are trying
                  to scrape is not supported by Mealie or it's scraper library.
                  <v-text-field
                    v-model="recipeUrl"
                    :label="$t('new-recipe.recipe-url')"
                    validate-on-blur
                    autofocus
                    filled
                    clearable
                    rounded
                    class="rounded-lg mt-2"
                    :rules="[validators.url]"
                    :hint="$t('new-recipe.url-form-hint')"
                    persistent-hint
                  ></v-text-field>
                </v-card-text>
                <v-card-actions class="justify-center">
                  <div style="width: 250px">
                    <BaseButton rounded block type="submit" color="info" :loading="loading">
                      <template #icon>
                        {{ $globals.icons.robot }}
                      </template>
                      Debug
                    </BaseButton>
                  </div>
                </v-card-actions>
              </v-card>
            </v-form>
          </v-tab-item>
        </v-tabs-items>
      </section>
      <v-divider class="mt-5"></v-divider>
    </v-container>

    <v-container tag="section">
      <!--  Debug Extras -->
      <section v-if="debugData && tab === 'debug'">
        <v-checkbox v-model="debugTreeView" label="Tree View"></v-checkbox>
        <VJsoneditor
          v-model="debugData"
          class="primary"
          :options="{
            mode: debugTreeView ? 'tree' : 'code',
            search: false,
            indentation: 4,
            mainMenuBar: false,
          }"
          height="700px"
        />
      </section>
    </v-container>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, ref, useRouter, useContext } from "@nuxtjs/composition-api";
// @ts-ignore No Types for v-jsoneditor
import VJsoneditor from "v-jsoneditor";
import { useApiSingleton } from "~/composables/use-api";
import { validators } from "~/composables/use-validators";
import { Recipe } from "~/types/api-types/recipe";
export default defineComponent({
  components: { VJsoneditor },
  setup() {
    const state = reactive({
      error: false,
      loading: false,
    });

    // @ts-ignore - $globals not found in type definition
    const { $globals } = useContext();

    const tabs = [
      {
        icon: $globals.icons.link,
        text: "Import with URL",
        value: "url",
      },
      {
        icon: $globals.icons.edit,
        text: "Create Recipe",
        value: "new",
      },
      {
        icon: $globals.icons.zip,
        text: "Import with .zip",
        value: "zip",
      },
      {
        icon: $globals.icons.robot,
        text: "Debug Scraper",
        value: "debug",
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
    // Recipe Debug URL Scraper
    // @ts-ignore

    const debugTreeView = ref(false);

    const debugData = ref<Recipe | null>(null);

    async function debugUrl(url: string) {
      state.loading = true;

      const { data } = await api.recipes.testCreateOneUrl(url);

      state.loading = false;
      debugData.value = data;
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
      debugTreeView,
      tabs,
      domCreateByName,
      domUrlForm,
      newRecipeName,
      newRecipeZip,
      debugUrl,
      debugData,
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
        // @ts-ignore
        this.$router.replace({ query: { ...this.$route.query, tab } });
      },
      get() {
        // @ts-ignore
        return this.$route.query.tab;
      },
    },
    recipeUrl: {
      set(recipe_import_url) {
        // @ts-ignore
        this.$router.replace({ query: { ...this.$route.query, recipe_import_url } });
      },
      get() {
        // @ts-ignore
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
