<template>
  <v-form ref="form">
    <v-card-text>
      <v-row dense>
        <v-col cols="3"></v-col>
        <v-col>
          <v-file-input
            v-model="fileObject"
            :label="$t('general.image-file')"
            truncate-length="30"
            @change="uploadImage"
          ></v-file-input>
        </v-col>
        <v-col cols="3"></v-col>
      </v-row>
      <v-row dense>
        <v-col>
          <v-text-field
            :label="$t('recipe.total-time')"
            v-model="value.totalTime"
          ></v-text-field>
        </v-col>
        <v-col
          ><v-text-field
            :label="$t('recipe.prep-time')"
            v-model="value.prepTime"
          ></v-text-field
        ></v-col>
        <v-col
          ><v-text-field
            :label="$t('recipe.perform-time')"
            v-model="value.performTime"
          ></v-text-field
        ></v-col>
      </v-row>
      <v-text-field
        class="my-3"
        :label="$t('recipe.recipe-name')"
        v-model="value.name"
        :rules="[rules.required]"
      >
      </v-text-field>
      <v-textarea
        auto-grow
        min-height="100"
        :label="$t('recipe.description')"
        v-model="value.description"
      >
      </v-textarea>
      <div class="my-2"></div>
      <v-row dense disabled>
        <v-col sm="4">
          <v-text-field
            :label="$t('recipe.servings')"
            v-model="value.recipeYield"
            class="rounded-sm"
          >
          </v-text-field>
        </v-col>
        <v-spacer></v-spacer>
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
          <h2 class="mb-4">{{ $t("recipe.ingredients") }}</h2>
          <draggable
            v-model="value.recipeIngredient"
            @start="drag = true"
            @end="drag = false"
          >
            <transition-group
              type="transition"
              :name="!drag ? 'flip-list' : null"
            >
              <div
                v-for="(ingredient, index) in value.recipeIngredient"
                :key="generateKey('ingredient', index)"
              >
                <v-row align="center">
                  <v-text-field
                    class="mr-2"
                    :label="$t('recipe.ingredient')"
                    v-model="value.recipeIngredient[index]"
                    append-outer-icon="mdi-menu"
                    mdi-move-resize
                    solo
                    dense
                  >
                    <v-icon
                      class="mr-n1"
                      slot="prepend"
                      color="error"
                      @click="removeIngredient(index)"
                    >
                      mdi-delete
                    </v-icon>
                  </v-text-field>
                </v-row>
              </div>
            </transition-group>
          </draggable>

          <v-btn color="secondary" fab dark small @click="addIngredient">
            <v-icon>mdi-plus</v-icon>
          </v-btn>
          <BulkAdd @bulk-data="appendIngredients" />

          <h2 class="mt-6">{{ $t("recipe.categories") }}</h2>
          <v-combobox
            dense
            multiple
            chips
            item-color="secondary"
            deletable-chips
            v-model="value.recipeCategory"
            hide-selected
            :items="categories"
            text="name"
            :search-input.sync="categoriesSearchInput"
            @change="categoriesSearchInput = ''"
          >
            <template v-slot:selection="data">
              <v-chip
                :input-value="data.selected"
                close
                @click:close="removeCategory(data.index)"
                color="secondary"
                dark
              >
                {{ data.item }}
              </v-chip>
            </template>
          </v-combobox>

          <h2 class="mt-4">{{ $t("recipe.tags") }}</h2>
          <v-combobox
            dense
            multiple
            chips
            deletable-chips
            v-model="value.tags"
            hide-selected
            :items="tags"
            :search-input.sync="tagsSearchInput"
            @change="tagssSearchInput = ''"
          >
            <template v-slot:selection="data">
              <v-chip
                :input-value="data.selected"
                close
                @click:close="removeTags(data.index)"
                color="secondary"
                dark
              >
                {{ data.item }}
              </v-chip>
            </template>
          </v-combobox>

          <h2 class="my-4">{{ $t("recipe.notes") }}</h2>
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
                  :label="$t('recipe.title')"
                  v-model="value.notes[index]['title']"
                ></v-text-field>
              </v-row>

              <v-textarea
                auto-grow
                :label="$t('recipe.note')"
                v-model="value.notes[index]['text']"
              >
              </v-textarea>
            </v-card-text>
          </v-card>
          <v-btn class="mt-1" color="secondary" fab dark small @click="addNote">
            <v-icon>mdi-plus</v-icon>
          </v-btn>
          <ExtrasEditor :extras="value.extras" @save="saveExtras" />
        </v-col>

        <v-divider class="my-divider" :vertical="true"></v-divider>

        <v-col cols="12" sm="12" md="8" lg="8">
          <h2 class="mb-4">{{ $t("recipe.instructions") }}</h2>
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
                    <v-icon color="error">mdi-delete</v-icon>
                  </v-btn>
                  {{ $t("recipe.step-index", { step: index + 1 }) }}
                </v-card-title>
                <v-card-text>
                  <v-textarea
                    auto-grow
                    dense
                    v-model="value.recipeInstructions[index]['text']"
                    :key="generateKey('instructions', index)"
                  >
                  </v-textarea>
                </v-card-text>
              </v-card>
            </v-hover>
          </div>
          <v-btn color="secondary" fab dark small @click="addStep">
            <v-icon>mdi-plus</v-icon>
          </v-btn>
          <BulkAdd @bulk-data="appendSteps" />
          <v-text-field
            v-model="value.orgURL"
            class="mt-10"
            :label="$t('recipe.original-url')"
          ></v-text-field>
        </v-col>
      </v-row>
    </v-card-text>
  </v-form>
</template>

<script>
import draggable from "vuedraggable";
import api from "@/api";
import utils from "@/utils";
import BulkAdd from "./BulkAdd";
import ExtrasEditor from "./ExtrasEditor";
export default {
  components: {
    BulkAdd,
    ExtrasEditor,
    draggable,
  },
  props: {
    value: Object,
  },
  data() {
    return {
      drag: false,
      fileObject: null,
      rules: {
        required: v => !!v || this.$i18n.t("recipe.key-name-required"),
        whiteSpace: v =>
          !v ||
          v.split(" ").length <= 1 ||
          this.$i18n.t("recipe.no-white-space-allowed"),
      },
      categoriesSearchInput: "",
      tagsSearchInput: "",
      categories: [],
      tags: [],
    };
  },
  mounted() {
    this.getCategories();
  },
  methods: {
    async getCategories() {
      let response = await api.categories.get_all();
      this.categories = response.map(cat => cat.name);
    },
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
      steps.forEach(element => {
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
    removeCategory(index) {
      this.value.recipeCategory.splice(index, 1);
    },
    removeTags(index) {
      this.value.tags.splice(index, 1);
    },
    saveExtras(extras) {
      this.value.extras = extras;
    },
    validateRecipe() {
      if (this.$refs.form.validate()) {
        return true;
      } else {
        return false;
      }
    },
  },
};
</script>

<style>
.disabled-card {
  opacity: 0.5;
}
.my-divider {
  margin: 0 -1px;
}
</style>