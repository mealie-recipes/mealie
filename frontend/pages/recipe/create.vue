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
            <BaseOverflowButton v-model="tab" rounded :items="tabs"> </BaseOverflowButton>
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
                </v-card-text>
                <v-card-actions class="justify-center">
                  <div style="width: 250px">
                    <BaseButton :disabled="recipeUrl === null" rounded block type="submit" :loading="loading" />
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
                    :prepend-inner-icon="$globals.icons.primary"
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
                  <BaseButton
                    :disabled="newRecipeName === ''"
                    rounded
                    block
                    :loading="loading"
                    @click="createByName(newRecipeName)"
                  />
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
                    <BaseButton
                      :disabled="newRecipeZip === null"
                      large
                      rounded
                      block
                      :loading="loading"
                      @click="createByZip"
                    />
                  </div>
                </v-card-actions>
              </v-card>
            </v-form>
          </v-tab-item>

          <!-- Create By Zip -->
          <v-tab-item value="debug" eager>
            <v-form ref="domUrlForm" @submit.prevent="debugUrl(recipeUrl)">
              <v-card flat>
                <v-card-title class="headline"> Recipe Debugger </v-card-title>
                <v-card-text>
                  Grab the URL of the recipe you want to debug and paste it here. The URL will be scraped by the recipe
                  scraper and the results will be displayed. If you don't see any data returned, the site you are trying
                  to scrape is not supported by Mealie or it's scraper library.
                  <v-text-field
                    v-model="recipeUrl"
                    :label="$t('new-recipe.recipe-url')"
                    validate-on-blur
                    :prepend-inner-icon="$globals.icons.link"
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
                    <BaseButton
                      :disabled="recipeUrl === null"
                      rounded
                      block
                      type="submit"
                      color="info"
                      :loading="loading"
                    >
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

          <v-tab-item value="bulk" eager>
            <v-card flat>
              <v-card-title class="headline"> Recipe Bulk Importer </v-card-title>
              <v-card-text>
                The Bulk recipe importer allows you to import multiple recipes at once by queing the sites on the
                backend and running the task in the background. This can be useful when initially migrating to Mealie,
                or when you want to import a large number of recipes.
              </v-card-text>
            </v-card>
          </v-tab-item>
        </v-tabs-items>
      </section>
      <v-divider class="mt-5"></v-divider>
    </v-container>

    <v-container tag="section">
      <!--  Debug Extras -->
      <section v-if="debugData && tab === 'debug'">
        <v-checkbox v-model="debugTreeView" label="Tree View"></v-checkbox>
        <LazyRecipeJsonEditor
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
      <!--  Debug Extras -->
      <section v-else-if="tab === 'bulk'" class="mt-2">
        <v-row v-for="(bulkUrl, idx) in bulkUrls" :key="'bulk-url' + idx" class="my-1" dense>
          <v-col cols="12" xs="12" sm="12" md="12">
            <v-text-field
              v-model="bulkUrls[idx].url"
              :label="$t('new-recipe.recipe-url')"
              dense
              single-line
              validate-on-blur
              autofocus
              filled
              hide-details
              clearable
              :prepend-inner-icon="$globals.icons.link"
              rounded
              class="rounded-lg"
            >
              <template #append>
                <v-btn color="error" icon x-small @click="bulkUrls.splice(idx, 1)">
                  <v-icon>
                    {{ $globals.icons.delete }}
                  </v-icon>
                </v-btn>
              </template>
            </v-text-field>
          </v-col>
          <v-col cols="12" xs="12" sm="6">
            <RecipeCategoryTagSelector
              v-model="bulkUrls[idx].categories"
              validate-on-blur
              autofocus
              single-line
              filled
              hide-details
              dense
              clearable
              rounded
              class="rounded-lg"
            ></RecipeCategoryTagSelector>
          </v-col>
          <v-col cols="12" xs="12" sm="6">
            <RecipeCategoryTagSelector
              v-model="bulkUrls[idx].tags"
              validate-on-blur
              autofocus
              tag-selector
              hide-details
              filled
              dense
              single-line
              clearable
              rounded
              class="rounded-lg"
            ></RecipeCategoryTagSelector>
          </v-col>
        </v-row>
        <v-card-actions class="justify-end">
          <BaseButton
            delete
            @click="
              bulkUrls = [];
              lockBulkImport = false;
            "
          >
            Clear
          </BaseButton>
          <v-spacer></v-spacer>
          <BaseButton color="info" @click="bulkUrls.push({ url: '', categories: [], tags: [] })">
            <template #icon> {{ $globals.icons.createAlt }} </template> New
          </BaseButton>
          <BaseButton :disabled="bulkUrls.length === 0 || lockBulkImport" @click="bulkCreate">
            <template #icon> {{ $globals.icons.check }} </template> Submit
          </BaseButton>
        </v-card-actions>
      </section>
    </v-container>

    <v-container v-if="$auth.user.advanced" class="narrow-container d-flex justify-end">
      <v-btn outlined rounded to="/group/data/migrations"> Looking For Migrations? </v-btn>
    </v-container>
  </div>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  ref,
  useRouter,
  useContext,
  computed,
  useRoute,
} from "@nuxtjs/composition-api";
import { AxiosResponse } from "axios";
import { useUserApi } from "~/composables/api";
import RecipeCategoryTagSelector from "~/components/Domain/Recipe/RecipeCategoryTagSelector.vue";
import { validators } from "~/composables/use-validators";
import { Recipe } from "~/types/api-types/recipe";
import { alert } from "~/composables/use-toast";
import { VForm } from "~/types/vuetify";
import { MenuItem } from "~/components/global/BaseOverflowButton.vue";

export default defineComponent({
  components: { RecipeCategoryTagSelector },
  setup() {
    const state = reactive({
      error: false,
      loading: false,
    });

    const { $globals } = useContext();

    const tabs: MenuItem[] = [
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
        icon: $globals.icons.link,
        text: "Bulk URL Import",
        value: "bulk",
      },
      {
        icon: $globals.icons.robot,
        text: "Debug Scraper",
        value: "debug",
      },
    ];

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

    const tab = computed({
      set(tab: string) {
        router.replace({ query: { ...route.value.query, tab } });
      },
      get() {
        return route.value.query.tab as string;
      },
    });

    const recipeUrl = computed({
      set(recipe_import_url: string) {
        recipe_import_url = recipe_import_url.trim();
        router.replace({ query: { ...route.value.query, recipe_import_url } });
      },
      get() {
        return route.value.query.recipe_import_url as string;
      },
    });

    // ===================================================
    // Recipe Debug URL Scraper

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
    const domUrlForm = ref<VForm | null>(null);

    async function createByUrl(url: string) {
      if (!domUrlForm.value?.validate() || url === "") {
        console.log("Invalid URL", url);
        return;
      }
      state.loading = true;
      const { response } = await api.recipes.createOneByUrl(url);
      handleResponse(response);
    }

    // ===================================================
    // Recipe Create By Name
    const newRecipeName = ref("");
    const domCreateByName = ref<VForm | null>(null);

    async function createByName(name: string) {
      if (!domCreateByName.value?.validate() || name === "") {
        return;
      }
      const { response } = await api.recipes.createOne({ name });
      // TODO createOne claims to return a Recipe, but actually the API only returns a string
      // @ts-ignore See above
      handleResponse(response, true);
    }

    // ===================================================
    // Recipe Import From Zip File
    const newRecipeZip = ref<File | null>(null);
    const newRecipeZipFileName = "archive";

    async function createByZip() {
      if (!newRecipeZip.value) {
        return;
      }
      const formData = new FormData();
      formData.append(newRecipeZipFileName, newRecipeZip.value);

      const { response } = await api.upload.file("/api/recipes/create-from-zip", formData);
      handleResponse(response);
    }

    // ===================================================
    // Bulk Importer

    const bulkUrls = ref([{ url: "", categories: [], tags: [] }]);
    const lockBulkImport = ref(false);

    async function bulkCreate() {
      if (bulkUrls.value.length === 0) {
        return;
      }

      const { response } = await api.recipes.createManyByUrl({ imports: bulkUrls.value });

      if (response?.status === 202) {
        alert.success("Bulk Import process has started");
        lockBulkImport.value = true;
      } else {
        alert.error("Bulk import process has failed");
      }
    }

    return {
      tab,
      recipeUrl,
      bulkCreate,
      bulkUrls,
      lockBulkImport,
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
});
</script>

<style>
.force-white > a {
  color: white !important;
}
</style>
