<template>
  <v-container>
    <v-card v-if="skeleton" :color="`white ${theme.isDark ? 'darken-2' : 'lighten-4'}`" class="pa-3">
      <v-skeleton-loader class="mx-auto" height="700px" type="card"></v-skeleton-loader>
    </v-card>
    <NoRecipe v-else-if="loadFailed" />
    <v-card v-else-if="!loadFailed" id="myRecipe" class="d-print-none">
      <v-img height="400" :src="getImage(recipeDetails.slug)" class="d-print-none" :key="imageKey">
        <RecipeTimeCard
          :class="isMobile ? undefined : 'force-bottom'"
          :prepTime="recipeDetails.prepTime"
          :totalTime="recipeDetails.totalTime"
          :performTime="recipeDetails.performTime"
        />
      </v-img>
      <EditorButtonRow
        v-if="loggedIn"
        :open="showIcons"
        @json="jsonEditor = true"
        @editor="
          jsonEditor = false;
          form = true;
        "
        @save="saveRecipe"
        @delete="deleteRecipe"
        class="sticky"
      />

      <RecipeViewer v-if="!form" :recipe="recipeDetails" />
      <VJsoneditor
        @error="logError()"
        class="mt-10"
        v-else-if="showJsonEditor"
        v-model="recipeDetails"
        height="1500px"
        :options="jsonEditorOptions"
      />
      <RecipeEditor v-else v-model="recipeDetails" ref="recipeEditor" @upload="getImageFile" />
    </v-card>
    <PrintView :recipe="recipeDetails" />
  </v-container>
</template>

<script>
import { api } from "@/api";
import VJsoneditor from "v-jsoneditor";
import RecipeViewer from "@/components/Recipe/RecipeViewer";
import PrintView from "@/components/Recipe/PrintView";
import RecipeEditor from "@/components/Recipe/RecipeEditor";
import RecipeTimeCard from "@/components/Recipe/RecipeTimeCard.vue";
import EditorButtonRow from "@/components/Recipe/EditorButtonRow";
import NoRecipe from "@/components/Fallbacks/NoRecipe";
import { user } from "@/mixins/user";
import { router } from "@/routes";

export default {
  components: {
    VJsoneditor,
    RecipeViewer,
    RecipeEditor,
    EditorButtonRow,
    RecipeTimeCard,
    PrintView,
    NoRecipe,
  },
  mixins: [user],
  inject: {
    theme: {
      default: { isDark: false },
    },
  },
  data() {
    return {
      loadFailed: false,
      skeleton: true,
      form: false,
      jsonEditor: false,
      jsonEditorOptions: {
        mode: "code",
        search: false,
        mainMenuBar: false,
      },
      // Recipe Details //
      recipeDetails: {
        name: "",
        description: "",
        image: "",
        recipeYield: "",
        recipeIngredient: [],
        recipeInstructions: [],
        slug: "",
        filePath: "",
        url: "",
        tags: [],
        categories: [],
        dateAdded: "",
        notes: [],
        rating: 0,
      },
      imageKey: 1,
    };
  },

  async mounted() {
    await this.getRecipeDetails();

    this.jsonEditor = false;
    this.form = this.$route.query.edit === "true" && this.loggedIn;

    if (this.$route.query.print) {
      this.printPage();
      this.$router.push(this.$route.path);
    }
  },

  watch: {
    $route: function() {
      this.getRecipeDetails();
    },
  },

  computed: {
    isMobile() {
      return this.$vuetify.breakpoint.name === "xs";
    },
    currentRecipe() {
      return this.$route.params.recipe;
    },
    edit() {
      return true;
    },
    showIcons() {
      return this.form;
    },
    showJsonEditor() {
      if ((this.form === true) & (this.jsonEditor === true)) {
        return true;
      } else {
        return false;
      }
    },
  },
  methods: {
    getImageFile(fileObject) {
      this.fileObject = fileObject;
      this.saveImage();
    },
    async getRecipeDetails() {
      if (this.currentRecipe === "null") {
        this.skeleton = false;
        this.loadFailed = true;
        return;
      }

      this.recipeDetails = await api.recipes.requestDetails(this.currentRecipe);
      this.skeleton = false;
    },
    getImage(image) {
      if (image) {
        return api.recipes.recipeImage(image) + "?&rnd=" + this.imageKey;
      }
    },
    async deleteRecipe() {
      let response = await api.recipes.delete(this.recipeDetails.slug);
      if (response) {
        router.push(`/`);
      }
    },
    validateRecipe() {
      if (this.jsonEditor) {
        return true;
      } else {
        return this.$refs.recipeEditor.validateRecipe();
      }
    },
    async saveImage(overrideSuccessMsg = false) {
      if (this.fileObject) {
        if (api.recipes.updateImage(this.recipeDetails.slug, this.fileObject, overrideSuccessMsg)) {
          this.imageKey += 1;
        }
      }
    },
    async saveRecipe() {
      if (this.validateRecipe()) {
        let slug = await api.recipes.update(this.recipeDetails);

        if (this.fileObject) {
          this.saveImage(true);
        }

        this.form = false;
        if (slug != this.recipeDetails.slug) {
          this.$router.push(`/recipe/${slug}`);
        }
      }
    },
    printPage() {
      window.print();
    },
  },
};
</script>

<style>
.card-btn {
  margin-top: -10px;
}
.disabled-card {
  opacity: 0.5;
}

.force-bottom {
  position: absolute;
  width: 100%;
  bottom: 0;
}
.sticky {
  position: sticky !important;
  top: 0;
  z-index: 2;
}
</style>
