<template>
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
    <ButtonRow
      :open="showIcons"
      @json="jsonEditor = true"
      @editor="
        jsonEditor = false;
        form = true;
      "
      @save="saveRecipe"
      @delete="deleteRecipe"
    />

    <RecipeViewer
      v-if="!form"
      :name="recipeDetails.name"
      :ingredients="recipeDetails.recipeIngredient"
      :description="recipeDetails.description"
      :instructions="recipeDetails.recipeInstructions"
      :tags="recipeDetails.tags"
      :categories="recipeDetails.categories"
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
    <RecipeEditor v-else v-model="recipeDetails" @upload="getImageFile" />
  </v-card>
</template>

<script>
import api from "../api";
import utils from "../utils";
import VJsoneditor from "v-jsoneditor";
import RecipeViewer from "../components/Recipe/RecipeViewer";
import RecipeEditor from "../components/Recipe/RecipeEditor";
import RecipeTimeCard from "../components/Recipe/RecipeTimeCard.vue";
import ButtonRow from "../components/UI/ButtonRow";

export default {
  components: {
    VJsoneditor,
    RecipeViewer,
    RecipeEditor,
    ButtonRow,
    RecipeTimeCard,
  },
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
    $route: function () {
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
    async saveRecipe() {
      let slug = await api.recipes.update(this.recipeDetails);

      if (this.fileObject) {
        await api.recipes.updateImage(this.recipeDetails.slug, this.fileObject);
      }

      this.form = false;
      this.imageKey += 1;
      this.$router.push(`/recipe/${slug}`);
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
</style>