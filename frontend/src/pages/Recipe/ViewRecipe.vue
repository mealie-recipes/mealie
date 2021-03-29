<template>
  <v-container>
    <v-card id="myRecipe">
      <v-img
        height="400"
        :src="getImage(recipeDetails.image)"
        class="d-print-none"
        :key="imageKey"
      >
        <RecipeTimeCard
          class="force-bottom"
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

      <RecipeViewer
        v-if="!form"
        :name="recipeDetails.name"
        :ingredients="recipeDetails.recipeIngredient"
        :description="recipeDetails.description"
        :instructions="recipeDetails.recipeInstructions"
        :tags="recipeDetails.tags"
        :categories="recipeDetails.recipeCategory"
        :notes="recipeDetails.notes"
        :rating="recipeDetails.rating"
        :yields="recipeDetails.recipeYield"
        :orgURL="recipeDetails.orgURL"
      />
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
        ref="recipeEditor"
        @upload="getImageFile"
      />
    </v-card>
  </v-container>
</template>

<script>
import { api } from "@/api";
import utils from "@/utils";
import VJsoneditor from "v-jsoneditor";
import RecipeViewer from "@/components/Recipe/RecipeViewer";
import RecipeEditor from "@/components/Recipe/RecipeEditor";
import RecipeTimeCard from "@/components/Recipe/RecipeTimeCard.vue";
import EditorButtonRow from "@/components/Recipe/EditorButtonRow";
import { user } from "@/mixins/user";

export default {
  components: {
    VJsoneditor,
    RecipeViewer,
    RecipeEditor,
    EditorButtonRow,
    RecipeTimeCard,
  },
  mixins: [user],
  data() {
    return {
      // currentRecipe: this.$route.params.recipe,
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
  mounted() {
    this.getRecipeDetails();
  },

  watch: {
    $route: function() {
      this.getRecipeDetails();
    },
  },

  computed: {
    currentRecipe() {
      return this.$route.params.recipe;
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
    },
    async getRecipeDetails() {
      this.recipeDetails = await api.recipes.requestDetails(this.currentRecipe);
      this.form = false;
    },
    getImage(image) {
      if (image) {
        return utils.getImageURL(image) + "?rnd=" + this.imageKey;
      }
    },
    deleteRecipe() {
      api.recipes.delete(this.recipeDetails.slug);
    },
    validateRecipe() {
      if (this.jsonEditor) {
        return true;
      } else {
        return this.$refs.recipeEditor.validateRecipe();
      }
    },
    async saveRecipe() {
      if (this.validateRecipe()) {
        let slug = await api.recipes.update(this.recipeDetails);

        if (this.fileObject) {
          await api.recipes.updateImage(
            this.recipeDetails.slug,
            this.fileObject
          );
        }

        this.form = false;
        this.imageKey += 1;
        if (slug != this.recipeDetails.slug) {
          this.$router.push(`/recipe/${slug}`);
        }
      }
    },
    showForm() {
      this.form = true;
      this.jsonEditor = false;
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