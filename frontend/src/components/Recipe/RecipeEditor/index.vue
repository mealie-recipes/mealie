<template>
  <v-form ref="form">
    <v-card-text>
      <v-row dense>
        <ImageUploadBtn
          class="my-1"
          @upload="uploadImage"
          :slug="value.slug"
          @refresh="$emit('upload')"
        />
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
        :rules="[existsRule]"
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
            handle=".handle"
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
                  <v-textarea
                    class="mr-2"
                    :label="$t('recipe.ingredient')"
                    v-model="value.recipeIngredient[index]"
                    mdi-move-resize
                    auto-grow
                    solo
                    dense
                    rows="1"
                  >
                    <template slot="append-outer">
                      <v-icon class="handle">mdi-arrow-up-down</v-icon>
                    </template>
                    <v-icon
                      class="mr-n1"
                      slot="prepend"
                      color="error"
                      @click="removeByIndex(value.recipeIngredient, index)"
                    >
                      mdi-delete
                    </v-icon>
                  </v-textarea>
                </v-row>
              </div>
            </transition-group>
          </draggable>

          <div class="d-flex row justify-end">
            <BulkAdd @bulk-data="addIngredient" class="mr-2" />
            <v-btn color="secondary" dark @click="addIngredient" class="mr-4">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </div>

          <h2 class="mt-6">{{ $t("recipe.categories") }}</h2>
          <CategoryTagSelector
            :return-object="false"
            v-model="value.recipeCategory"
            :show-add="true"
            :show-label="false"
          />

          <h2 class="mt-4">{{ $t("recipe.tags") }}</h2>
          <CategoryTagSelector
            :return-object="false"
            v-model="value.tags"
            :show-add="true"
            :tag-selector="true"
            :show-label="false"
          />

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
                  @click="removeByIndex(value.notes, index)"
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
          <div class="d-flex justify-end">
            <v-btn class="mt-1" color="secondary" dark @click="addNote">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </div>
          <Nutrition v-model="value.nutrition" :edit="true" />
          <Assets v-model="value.assets" :edit="true" />
          <ExtrasEditor :extras="value.extras" @save="saveExtras" />
        </v-col>

        <v-divider class="my-divider" :vertical="true"></v-divider>

        <v-col cols="12" sm="12" md="8" lg="8">
          <Instructions v-model="value.recipeInstructions" :edit="true" />
          <div class="d-flex row justify-end mt-2">
            <BulkAdd @bulk-data="appendSteps" class="mr-2" />
            <v-btn color="secondary" dark @click="addStep" class="mr-4">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </div>

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
const UPLOAD_EVENT = "upload";
import draggable from "vuedraggable";
import utils from "@/utils";
import BulkAdd from "@/components/Recipe/Parts/Helpers/BulkAdd";
import ExtrasEditor from "./ExtrasEditor";
import CategoryTagSelector from "@/components/FormHelpers/CategoryTagSelector";
import ImageUploadBtn from "@/components/Recipe/Parts/Helpers/ImageUploadBtn";
import { validators } from "@/mixins/validators";
import Nutrition from "@/components/Recipe/Parts/Nutrition";
import Instructions from "@/components/Recipe/Parts/Instructions";
import Assets from "@/components/Recipe/Parts/Assets.vue";
export default {
  components: {
    BulkAdd,
    ExtrasEditor,
    draggable,
    CategoryTagSelector,
    Nutrition,
    ImageUploadBtn,
    Instructions,
    Assets,
  },
  props: {
    value: Object,
  },
  mixins: [validators],
  data() {
    return {
      drag: false,
      fileObject: null,
      lastTitleIndex: 0,
    };
  },
  methods: {
    validateTitle(title) {
      return !(title === null || title === "");
    },
    uploadImage(fileObject) {
      this.$emit(UPLOAD_EVENT, fileObject);
    },
    toggleDisabled(stepIndex) {
      if (this.disabledSteps.includes(stepIndex)) {
        const index = this.disabledSteps.indexOf(stepIndex);
        if (index !== -1) {
          this.disabledSteps.splice(index, 1);
        }
      } else {
        this.disabledSteps.push(stepIndex);
      }
    },
    isDisabled(stepIndex) {
      return this.disabledSteps.includes(stepIndex) ? "disabled-card" : null;
    },
    generateKey(item, index) {
      return utils.generateUniqueKey(item, index);
    },
    addIngredient(ingredients = null) {
      if (ingredients.length) {
        this.value.recipeIngredient.push(...ingredients);
      } else {
        this.value.recipeIngredient.push("");
      }
    },

    appendSteps(steps) {
      this.value.recipeInstructions.push(
        ...steps.map(x => ({
          text: x,
        }))
      );
    },
    addStep() {
      this.value.recipeInstructions.push({ text: "" });
    },
    addNote() {
      this.value.notes.push({ text: "" });
    },
    saveExtras(extras) {
      this.value.extras = extras;
    },
    removeByIndex(list, index) {
      list.splice(index, 1);
    },
    validateRecipe() {
      return this.$refs.form.validate();
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