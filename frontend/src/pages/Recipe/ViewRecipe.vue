<template>
  <v-container>
    <v-card v-if="skeleton" :color="`white ${theme.isDark ? 'darken-2' : 'lighten-4'}`" class="pa-3">
      <v-skeleton-loader class="mx-auto" height="700px" type="card"></v-skeleton-loader>
    </v-card>
    <NoRecipe v-else-if="loadFailed" />
    <v-card v-else-if="!loadFailed" id="myRecipe" class="d-print-none">
      <v-img
        :height="hideImage ? '50' : imageHeight"
        @error="hideImage = true"
        :src="getImage(recipeDetails.slug)"
        class="d-print-none"
        :key="imageKey"
      >
        <FavoriteBadge class="ma-1" button-style v-if="loggedIn" :slug="recipeDetails.slug" show-always />
        <RecipeTimeCard
          :class="isMobile ? undefined : 'force-bottom'"
          :prepTime="recipeDetails.prepTime"
          :totalTime="recipeDetails.totalTime"
          :performTime="recipeDetails.performTime"
        />
      </v-img>
      <RecipePageActionMenu
        :slug="recipeDetails.slug"
        :name="recipeDetails.name"
        v-model="form"
        :logged-in="loggedIn"
        :open="showIcons"
        @close="form = false"
        @json="jsonEditor = !jsonEditor"
        @edit="
          jsonEditor = false;
          form = true;
        "
        @save="saveRecipe"
        @delete="deleteRecipe"
        class="ml-auto"
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
      <RecipeEditor
        v-else
        v-model="recipeDetails"
        :class="$vuetify.breakpoint.xs ? 'mt-5' : ''"
        ref="recipeEditor"
        @upload="getImageFile"
      />
    </v-card>
    <CommentsSection
      v-if="recipeDetails.settings && !recipeDetails.settings.disableComments"
      class="mt-2 d-print-none"
      :slug="recipeDetails.slug"
      :comments="recipeDetails.comments"
      @new-comment="getRecipeDetails"
      @update-comment="getRecipeDetails"
    />
    <PrintView :recipe="recipeDetails" />
  </v-container>
</template>

<script>
import RecipePageActionMenu from "@/components/Recipe/RecipePageActionMenu.vue";
import { api } from "@/api";
import FavoriteBadge from "@/components/Recipe/FavoriteBadge";
import RecipeViewer from "@/components/Recipe/RecipeViewer";
import PrintView from "@/components/Recipe/PrintView";
import RecipeEditor from "@/components/Recipe/RecipeEditor";
import RecipeTimeCard from "@/components/Recipe/RecipeTimeCard.vue";
import NoRecipe from "@/components/Fallbacks/NoRecipe";
import { user } from "@/mixins/user";
import { router } from "@/routes";
import CommentsSection from "@/components/Recipe/CommentSection";

export default {
  components: {
    VJsoneditor: () => import(/* webpackChunkName: "json-editor" */ "v-jsoneditor"),
    RecipeViewer,
    RecipeEditor,
    RecipeTimeCard,
    RecipePageActionMenu,
    PrintView,
    NoRecipe,
    FavoriteBadge,
    CommentsSection,
  },
  mixins: [user],
  inject: {
    theme: {
      default: { isDark: false },
    },
  },
  data() {
    return {
      hideImage: false,
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

  created() {
    this.getRecipeDetails();
    this.jsonEditor = false;
    this.form = this.$route.query.edit === "true" && this.loggedIn;
  },

  async mounted() {
    this.checkPrintRecipe();
  },

  watch: {
    $route: function() {
      this.getRecipeDetails();
      this.checkPrintRecipe();
    },
  },

  computed: {
    loggedIn() {
      return this.$store.getters.getIsLoggedIn;
    },
    isMobile() {
      return this.$vuetify.breakpoint.name === "xs";
    },
    imageHeight() {
      return this.isMobile ? "200" : "400";
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
    checkPrintRecipe() {
      if (this.$route.query.print) {
        this.printPage();
        this.$router.push(this.$route.path);
        this.$route.query.print = null;
      }
    },
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

      const [response, error] = await api.recipes.requestDetails(this.currentRecipe);

      if (error) {
        if (error.response.status === 401) router.push(`/login`);
        if (error.response.status === 404) router.push("/page-not-found");
      }

      this.recipeDetails = response.data;
      this.skeleton = false;
    },
    getImage(slug) {
      if (slug) {
        return api.recipes.recipeImage(slug, this.imageKey, this.recipeDetails.image);
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
        const newVersion = await api.recipes.updateImage(this.recipeDetails.slug, this.fileObject, overrideSuccessMsg);
        if (newVersion) {
          this.recipeDetails.image = newVersion.data.version;
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
        window.URL.revokeObjectURL(this.getImage(this.recipeDetails.slug));
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
