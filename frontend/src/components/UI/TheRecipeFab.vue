<template>
  <div class="text-center d-print-none">
    <v-dialog v-model="addRecipe" width="650" @click:outside="reset">
      <v-card :loading="processing">
        <v-app-bar dark color="primary mb-2">
          <v-icon large left v-if="!processing"> {{ $globals.icons.link }} </v-icon>
          <v-progress-circular v-else indeterminate color="white" large class="mr-2"> </v-progress-circular>

          <v-toolbar-title class="headline">
            {{ $t("new-recipe.from-url") }}
          </v-toolbar-title>

          <v-spacer></v-spacer>
        </v-app-bar>
        <v-form ref="urlForm" @submit.prevent="createRecipe">
          <v-card-text>
            <v-text-field
              v-model="recipeURL"
              :label="$t('new-recipe.recipe-url')"
              required
              validate-on-blur
              autofocus
              class="mt-1"
              :rules="[isValidWebUrl]"
              :hint="$t('new-recipe.url-form-hint')"
              persistent-hint
            ></v-text-field>

            <v-expand-transition>
              <v-alert v-if="error" color="error" class="mt-6 white--text">
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
                    Google ld+json Info
                  </a>
                  <a href="https://github.com/hay-kot/mealie/issues" target="_blank" rel="noreferrer nofollow">
                    GitHub Issues
                  </a>
                  <a href="https://schema.org/Recipe" target="_blank" rel="noreferrer nofollow">
                    Recipe Markup Specification
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
                    View Scraped Data
                  </v-btn>
                </div>
              </v-alert>
            </v-expand-transition>
          </v-card-text>

          <v-divider></v-divider>

          <v-card-actions>
            <v-btn color="grey" text @click="reset">
              <v-icon left> {{ $globals.icons.close }}</v-icon>
              {{ $t("general.close") }}
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn color="success" type="submit" :loading="processing">
              <v-icon left> {{ $globals.icons.create }} </v-icon>
              {{ $t("general.submit") }}
            </v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
    <BaseDialog
      title="Upload a Recipe"
      :titleIcon="$globals.icons.zip"
      :submit-text="$t('general.import')"
      ref="uploadZipDialog"
      @submit="uploadZip"
      :loading="processing"
    >
      <v-card-text class="mt-1 pb-0">

        Upload an individual .zip file exported from another Mealie instance. 

        <div class="headline mx-auto mb-0 pb-0 text-center">
          {{ this.fileName }}
        </div>
      </v-card-text>

      <v-card-actions>
        <TheUploadBtn class="mx-auto" :text-btn="false" @uploaded="setFile" :post="false"> </TheUploadBtn>
      </v-card-actions>
    </BaseDialog>
    <v-speed-dial v-model="fab" :open-on-hover="absolute" :fixed="absolute" :bottom="absolute" :right="absolute">
      <template v-slot:activator>
        <v-btn v-model="fab" :color="absolute ? 'accent' : 'white'" dark :icon="!absolute" :fab="absolute">
          <v-icon> {{ $globals.icons.createAlt }} </v-icon>
        </v-btn>
      </template>
      <v-tooltip left dark color="primary">
        <template v-slot:activator="{ on, attrs }">
          <v-btn fab dark small color="primary" v-bind="attrs" v-on="on" @click="addRecipe = true">
            <v-icon>{{ $globals.icons.link }} </v-icon>
          </v-btn>
        </template>
        <span>{{ $t("new-recipe.from-url") }}</span>
      </v-tooltip>
      <v-tooltip left dark color="accent">
        <template v-slot:activator="{ on, attrs }">
          <v-btn fab dark small color="accent" v-bind="attrs" v-on="on" @click="$router.push('/new')">
            <v-icon>{{ $globals.icons.edit }}</v-icon>
          </v-btn>
        </template>
        <span>{{ $t("general.new") }}</span>
      </v-tooltip>
      <v-tooltip left dark color="info">
        <template v-slot:activator="{ on, attrs }">
          <v-btn fab dark small color="info" v-bind="attrs" v-on="on" @click="openZipUploader">
            <v-icon>{{ $globals.icons.zip }}</v-icon>
          </v-btn>
        </template>
        <span>{{ $t("general.upload") }}</span>
      </v-tooltip>
    </v-speed-dial>
  </div>
</template>

<script>
import { api } from "@/api";
import TheUploadBtn from "@/components/UI/Buttons/TheUploadBtn.vue";
import BaseDialog from "@/components/UI/Dialogs/BaseDialog.vue";
export default {
  components: {
    TheUploadBtn,
    BaseDialog,
  },
  props: {
    absolute: {
      default: false,
    },
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
    };
  },

  mounted() {
    if (this.$route.query.recipe_import_url) {
      this.addRecipe = true;
      this.createRecipe();
    }
  },

  computed: {
    recipeURL: {
      set(recipe_import_url) {
        this.$router.replace({ query: { ...this.$route.query, recipe_import_url } });
      },
      get() {
        return this.$route.query.recipe_import_url || "";
      },
    },
    fileName() {
      return this.uploadData.file?.name || "";
    },
  },

  methods: {
    resetVars() {
      this.uploadData = {
        fileName: "archive",
        file: null,
      };
    },
    setFile(file) {
      this.uploadData.file = file;
      console.log("Uploaded");
    },
    openZipUploader() {
      this.resetVars();
      this.$refs.uploadZipDialog.open();
    },
    async uploadZip() {
      let formData = new FormData();
      formData.append(this.uploadData.fileName, this.uploadData.file);

      const response = await api.utils.uploadFile("/api/recipes/create-from-zip", formData);

      this.$router.push(`/recipe/${response.data.slug}`);
    },
    async createRecipe() {
      this.error = false;
      if (this.$refs.urlForm === undefined || this.$refs.urlForm.validate()) {
        this.processing = true;
        const response = await api.recipes.createByURL(this.recipeURL);
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
    reset() {
      this.fab = false;
      this.error = false;
      this.addRecipe = false;
      this.recipeURL = "";
      this.processing = false;
    },
    isValidWebUrl(url) {
      let regEx = /^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,256}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)$/gm;
      return regEx.test(url) ? true : "Must be a Valid URL";
    },
  },
};
</script>

<style>
.force-white > a {
  color: white !important;
}
</style>
