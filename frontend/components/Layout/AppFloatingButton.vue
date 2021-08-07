<template>
  <div class="text-center d-print-none">
    <BaseDialog
      ref="domImportFromUrlDialog"
      :title="$t('new-recipe.from-url')"
      :icon="$globals.icons.link"
      :submit-text="$t('general.create')"
      :loading="processing"
      width="600px"
      @submit="createOnByUrl"
    >
      <v-form ref="domImportFromUrlForm" @submit.prevent="createOnByUrl">
        <v-card-text>
          <v-text-field
            v-model="recipeURL"
            :label="$t('new-recipe.recipe-url')"
            validate-on-blur
            autofocus
            filled
            rounded
            class="rounded-lg"
            :rules="[validators.url]"
            :hint="$t('new-recipe.url-form-hint')"
            persistent-hint
          ></v-text-field>

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
                  white
                  outlined
                  :to="{ path: '/recipes/debugger', query: { test_url: recipeURL } }"
                  @click="addRecipe = false"
                >
                  <v-icon left> {{ $globals.icons.externalLink }} </v-icon>
                  {{ $t("new-recipe.view-scraped-data") }}
                </v-btn>
              </div>
            </v-alert>
          </v-expand-transition>
        </v-card-text>
      </v-form>
    </BaseDialog>
    <BaseDialog
      ref="domUploadZipDialog"
      :title="$t('new-recipe.upload-a-recipe')"
      :icon="$globals.icons.zip"
      :submit-text="$t('general.import')"
      :loading="processing"
      @submit="uploadZip"
    >
      <v-card-text class="mt-1 pb-0">
        {{ $t("new-recipe.upload-individual-zip-file") }}

        <div class="headline mx-auto mb-0 pb-0 text-center">
          {{ fileName }}
        </div>
      </v-card-text>

      <v-card-actions>
        <!-- <AppButtonUpload class="mx-auto" :text-btn="false" :post="false" @uploaded="setFile"> </AppButtonUpload> -->
      </v-card-actions>
    </BaseDialog>
    <BaseDialog
      ref="domCreateDialog"
      :icon="$globals.icons.primary"
      title="Create A Recipe"
      @submit="manualCreateRecipe()"
    >
      <v-card-text class="mt-5">
        <v-form>
          <AutoForm v-model="createRecipeData.form" :items="createRecipeData.items" />
        </v-form>
      </v-card-text>
    </BaseDialog>
    <v-speed-dial v-model="fab" :open-on-hover="absolute" :fixed="absolute" :bottom="absolute" :right="absolute">
      <template #activator>
        <v-btn v-model="fab" :color="absolute ? 'accent' : 'white'" dark :icon="!absolute" :fab="absolute">
          <v-icon> {{ $globals.icons.createAlt }} </v-icon>
        </v-btn>
      </template>

      <!-- Action Buttons -->
      <v-tooltip left dark color="primary">
        <template #activator="{ on, attrs }">
          <v-btn fab dark small color="primary" v-bind="attrs" v-on="on" @click="domImportFromUrlDialog.open()">
            <v-icon>{{ $globals.icons.link }} </v-icon>
          </v-btn>
        </template>
        <span>{{ $t("new-recipe.from-url") }}</span>
      </v-tooltip>
      <v-tooltip left dark color="accent">
        <template #activator="{ on, attrs }">
          <v-btn fab dark small color="accent" v-bind="attrs" v-on="on" @click="domCreateDialog.open()">
            <v-icon>{{ $globals.icons.edit }}</v-icon>
          </v-btn>
        </template>
        <span>{{ $t("general.new") }}</span>
      </v-tooltip>
      <v-tooltip left dark color="info">
        <template #activator="{ on, attrs }">
          <v-btn fab dark small color="info" v-bind="attrs" v-on="on" @click="domUploadZipDialog.open()">
            <v-icon>{{ $globals.icons.zip }}</v-icon>
          </v-btn>
        </template>
        <span>{{ $t("general.upload") }}</span>
      </v-tooltip>
    </v-speed-dial>
  </div>
</template>


<script lang="ts">
// import AppButtonUpload from "@/components/UI/Buttons/AppButtonUpload.vue";
import { defineComponent, ref } from "@nuxtjs/composition-api";
import { fieldTypes } from "~/composables/forms";
import { useApiSingleton } from "~/composables/use-api";
import { validators } from "~/composables/use-validators";

export default defineComponent({
  props: {
    absolute: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const domCreateDialog = ref(null);
    const domCreateForm = ref<VForm | null>(null);

    const domUploadZipDialog = ref(null);
    const domUploadZipForm = ref<VForm | null>(null);

    const domImportFromUrlDialog = ref(null);
    const domImportFromUrlForm = ref<VForm | null>(null);

    const api = useApiSingleton();

    return {
      domCreateDialog,
      domCreateForm,
      domUploadZipDialog,
      domUploadZipForm,
      domImportFromUrlDialog,
      domImportFromUrlForm,
      api,
      validators,
    };
  },
  data() {
    return {
      error: false,
      fab: false,
      addRecipe: false,
      processing: false,
      uploadData: {
        fileName: "archive",
        file: null,
      },
      createRecipeData: {
        items: [
          {
            label: "Recipe Name",
            varName: "name",
            type: fieldTypes.TEXT,
            rules: ["required"],
          },
        ],
        form: {
          name: "",
        },
      },
    };
  },

  computed: {
    recipeURL: {
      set(recipe_import_url: string) {
        this.$router.replace({ query: { ...this.$route.query, recipe_import_url } });
      },
      get(): string {
        return this.$route.query.recipe_import_url || "";
      },
    },
    fileName(): string {
      if (this.uploadData?.file?.name) {
        return this.uploadData.file.name;
      }
      return "";
    },
  },

  mounted() {
    if (this.$route.query.recipe_import_url) {
      this.addRecipe = true;
      this.createOnByUrl();
    }
  },

  methods: {
    reset() {
      this.fab = false;
      this.error = false;
      this.addRecipe = false;
      this.recipeURL = "";
      this.processing = false;
    },
    resetVars() {
      this.uploadData = {
        fileName: "archive",
        file: null,
      };
    },
    setFile(file: any) {
      this.uploadData.file = file;
      console.log("Uploaded");
    },
    async uploadZip() {
      const formData = new FormData();
      formData.append(this.uploadData.fileName, this.uploadData.file);

      const response = await this.api.utils.uploadFile("/api/recipes/create-from-zip", formData);

      this.$router.push(`/recipe/${response.data.slug}`);
    },
    async manualCreateRecipe() {
      await this.api.recipes.createOne({ name: this.createRecipeData.form.name });
    },
    async createOnByUrl() {
      this.error = false;
      console.log(this.domImportFromUrlForm?.validate());

      if (this.domImportFromUrlForm?.validate()) {
        this.processing = true;
        const response = await this.api.recipes.createOneByUrl(this.recipeURL);
        this.processing = false;
        if (response) {
          this.addRecipe = false;
          this.recipeURL = "";
          this.$router.push(`/recipe/${response.data}`);
        } else {
          this.error = true;
        }
      }
    },
  },
});
</script>
      
<style scoped>
</style>