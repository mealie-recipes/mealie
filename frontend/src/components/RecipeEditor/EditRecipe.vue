<template>
  <div>
    <v-card-text>
      <v-row dense>
        <v-col cols="3"></v-col>
        <v-col>
          <v-file-input
            v-model="fileObject"
            label="Image File"
            truncate-length="30"
            @change="uploadImage"
          ></v-file-input>
        </v-col>
        <v-col cols="3"></v-col>
      </v-row>
      <v-text-field class="my-3" label="Recipe Name" v-model="value.name">
      </v-text-field>
      <v-textarea height="100" label="Description" v-model="value.description">
      </v-textarea>
      <div class="my-2"></div>
      <v-row dense disabled>
        <v-col sm="5">
          <v-text-field
            label="Servings"
            v-model="value.recipeYield"
          >
          </v-text-field>
        </v-col>
        <v-col></v-col>
        <v-rating
          class="mr-2 align-end"
          color="secondary darken-1"
          background-color="secondary lighten-3"
          length="5"
          v-model="value.rating"
        ></v-rating>
      </v-row>
      <v-row>
        <v-col cols="12" sm="12" md="4" lg="4">
          <h2 class="mb-4">Ingredients</h2>
          <div
            v-for="(ingredient, index) in value.recipeIngredient"
            :key="generateKey('ingredient', index)"
          >
            <v-row align="center">
              <v-btn
                fab
                x-small
                color="white"
                class="mr-2"
                elevation="0"
                @click="removeIngredient(index)"
              >
                <v-icon color="error">mdi-delete</v-icon>
              </v-btn>
              <v-text-field
                label="Ingredient"
                v-model="value.recipeIngredient[index]"
              ></v-text-field>
            </v-row>
          </div>
          <v-btn color="secondary" fab dark small @click="addIngredient">
            <v-icon>mdi-plus</v-icon>
          </v-btn>
          <BulkAdd @bulk-data="appendIngredients" />

          <h2 class="mt-6">Categories</h2>
          <v-combobox
            dense
            multiple
            chips
            item-color="secondary"
            deletable-chips
            v-model="value.categories"
          >
            <template v-slot:selection="data">
              <v-chip :input-value="data.selected" close color="secondary" dark>
                {{ data.item }}
              </v-chip>
            </template>
          </v-combobox>

          <h2 class="mt-4">Tags</h2>
          <v-combobox dense multiple chips deletable-chips v-model="value.tags">
            <template v-slot:selection="data">
              <v-chip :input-value="data.selected" close color="secondary" dark>
                {{ data.item }}
              </v-chip>
            </template>
          </v-combobox>

          <h2 class="my-4">Notes</h2>
          <v-card
            class="mt-1"
            v-for="(note, index) in value.notes"
            :key="generateKey('note', index)"
          >
            <v-card-text>
              <v-row align="center">
                <v-btn
                  fab
                  x-small
                  color="white"
                  class="mr-2"
                  elevation="0"
                  @click="removeNote(index)"
                >
                  <v-icon color="error">mdi-delete</v-icon>
                </v-btn>
                <v-text-field
                  label="Title"
                  v-model="value.notes[index]['title']"
                ></v-text-field>
              </v-row>

              <v-textarea label="Note" v-model="value.notes[index]['text']">
              </v-textarea>
            </v-card-text>
          </v-card>
          <v-btn class="mt-1" color="secondary" fab dark small @click="addNote">
            <v-icon>mdi-plus</v-icon>
          </v-btn>
        </v-col>

        <v-divider class="my-divider" :vertical="true"></v-divider>

        <v-col cols="12" sm="12" md="8" lg="8">
          <h2 class="mb-4">Instructions</h2>
          <div v-for="(step, index) in value.recipeInstructions" :key="index">
            <v-hover v-slot="{ hover }">
              <v-card
                class="ma-1"
                :class="[{ 'on-hover': hover }]"
                :elevation="hover ? 12 : 2"
              >
                <v-card-title>
                  <v-btn
                    fab
                    x-small
                    color="white"
                    class="mr-2"
                    elevation="0"
                    @click="removeStep(index)"
                  >
                    <v-icon color="error">mdi-delete</v-icon> </v-btn
                  >Step: {{ index + 1 }}</v-card-title
                >
                <v-card-text>
                  <v-textarea
                    dense
                    v-model="value.recipeInstructions[index]['text']"
                    :key="generateKey('instructions', index)"
                  ></v-textarea>
                </v-card-text>
              </v-card>
            </v-hover>
          </div>
          <v-btn color="secondary" fab dark small @click="addStep">
            <v-icon>mdi-plus</v-icon>
          </v-btn>
          <BulkAdd @bulk-data="appendSteps" />
        </v-col>
      </v-row>
    </v-card-text>
  </div>
</template>

<script>
import api from "../../api";
import utils from "../../utils";
import BulkAdd from "./BulkAdd";
export default {
  components: {
    BulkAdd,
  },
  props: {
    value: Object,
  },
  data() {
    return {
      fileObject: null,
      content: this.value,
      disabledSteps: [],
      description: String,
      ingredients: Array,
      instructions: Array,
      categories: Array,
      tags: Array,
    };
  },
  methods: {
    uploadImage() {
      this.$emit("upload", this.fileObject);
    },
    async updateImage() {
      let slug = this.value.slug;
      api.recipes.updateImage(slug, this.fileObject);
    },
    toggleDisabled(stepIndex) {
      if (this.disabledSteps.includes(stepIndex)) {
        let index = this.disabledSteps.indexOf(stepIndex);
        if (index !== -1) {
          this.disabledSteps.splice(index, 1);
        }
      } else {
        this.disabledSteps.push(stepIndex);
      }
    },
    isDisabled(stepIndex) {
      if (this.disabledSteps.includes(stepIndex)) {
        return "disabled-card";
      } else {
        return;
      }
    },
    generateKey(item, index) {
      return utils.generateUniqueKey(item, index);
    },
    deleteRecipe() {
      this.$emit("delete");
    },

    appendIngredients(ingredients) {
      this.value.recipeIngredient.push(...ingredients);
    },
    addIngredient() {
      let list = this.value.recipeIngredient;
      list.push("");
    },

    removeIngredient(index) {
      this.value.recipeIngredient.splice(index, 1);
    },

    appendSteps(steps) {
      let processSteps = [];
      steps.forEach((element) => {
        processSteps.push({ text: element });
      });

      this.value.recipeInstructions.push(...processSteps);
    },
    addStep() {
      let list = this.value.recipeInstructions;
      list.push({ text: "" });
    },
    removeStep(index) {
      this.value.recipeInstructions.splice(index, 1);
    },

    addNote() {
      let list = this.value.notes;
      list.push({ text: "" });
    },
    removeNote(index) {
      this.value.notes.splice(index, 1);
    },
  },
};
</script>

<style>
.disabled-card {
  opacity: 50%;
}
.my-divider {
  margin: 0 -1px;
}
</style>