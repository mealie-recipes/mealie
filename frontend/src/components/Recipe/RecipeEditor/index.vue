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
        <SettingsMenu
          class="my-1 mx-1"
          @upload="uploadImage"
          :value="value.settings"
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
          <Ingredients :edit="true" v-model="value.recipeIngredient" />

          <h2 class="mt-6">{{ $t("recipe.categories") }}</h2>
          <CategoryTagSelector
            :return-object="false"
            v-model="value.recipeCategory"
            :show-add="true"
            :show-label="false"
          />

          <h2 class="mt-4">{{ $t("tag.tags") }}</h2>
          <CategoryTagSelector
            :return-object="false"
            v-model="value.tags"
            :show-add="true"
            :tag-selector="true"
            :show-label="false"
          />
          <Nutrition v-model="value.nutrition" :edit="true" />
          <Assets v-model="value.assets" :edit="true" :slug="value.slug" />
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
          <Notes :edit="true" v-model="value.notes" />

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
import BulkAdd from "@/components/Recipe/Parts/Helpers/BulkAdd";
import ExtrasEditor from "@/components/Recipe/Parts/Helpers/ExtrasEditor";
import CategoryTagSelector from "@/components/FormHelpers/CategoryTagSelector";
import ImageUploadBtn from "@/components/Recipe/Parts/Helpers/ImageUploadBtn";
import { validators } from "@/mixins/validators";
import Nutrition from "@/components/Recipe/Parts/Nutrition";
import Instructions from "@/components/Recipe/Parts/Instructions";
import Ingredients from "@/components/Recipe/Parts/Ingredients";
import Assets from "@/components/Recipe/Parts/Assets.vue";
import Notes from "@/components/Recipe/Parts/Notes.vue";
import SettingsMenu from "@/components/Recipe/Parts/Helpers/SettingsMenu.vue";
export default {
  components: {
    BulkAdd,
    ExtrasEditor,
    CategoryTagSelector,
    Nutrition,
    ImageUploadBtn,
    Instructions,
    Ingredients,
    Assets,
    Notes,
    SettingsMenu,
  },
  props: {
    value: Object,
  },
  mixins: [validators],
  data() {
    return {
      fileObject: null,
    };
  },
  methods: {
    uploadImage(fileObject) {
      this.$emit(UPLOAD_EVENT, fileObject);
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
    saveExtras(extras) {
      this.value.extras = extras;
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