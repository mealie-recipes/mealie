<template>
  <v-form ref="form">
    <v-card-text>
      <v-row dense>
        <ImageUploadBtn class="my-1" :slug="value.slug" @upload="uploadImage" @refresh="$emit('upload')" />
        <SettingsMenu class="my-1 mx-1" :value="value.settings" @upload="uploadImage" />
      </v-row>
      <v-row dense>
        <v-col>
          <v-text-field v-model="value.totalTime" :label="$t('recipe.total-time')"></v-text-field>
        </v-col>
        <v-col><v-text-field v-model="value.prepTime" :label="$t('recipe.prep-time')"></v-text-field></v-col>
        <v-col><v-text-field v-model="value.performTime" :label="$t('recipe.perform-time')"></v-text-field></v-col>
      </v-row>
      <v-text-field v-model="value.name" class="my-3" :label="$t('recipe.recipe-name')" :rules="[existsRule]">
      </v-text-field>
      <v-textarea v-model="value.description" auto-grow min-height="100" :label="$t('recipe.description')">
      </v-textarea>
      <div class="my-2"></div>
      <v-row dense disabled>
        <v-col sm="4">
          <v-text-field v-model="value.recipeYield" :label="$t('recipe.servings')" class="rounded-sm"> </v-text-field>
        </v-col>
        <v-spacer></v-spacer>
        <Rating v-model="value.rating" :emit-only="true" />
      </v-row>
      <v-row>
        <v-col cols="12" sm="12" md="4" lg="4">
          <Ingredients v-model="value.recipeIngredient" :edit="true" />
          <v-card class="mt-6">
            <v-card-title class="py-2">
              {{ $t("recipe.categories") }}
            </v-card-title>
            <v-divider class="mx-2"></v-divider>
            <v-card-text>
              <CategoryTagSelector
                v-model="value.recipeCategory"
                :return-object="false"
                :show-add="true"
                :show-label="false"
              />
            </v-card-text>
          </v-card>

          <v-card class="mt-2">
            <v-card-title class="py-2">
              {{ $t("tag.tags") }}
            </v-card-title>
            <v-divider class="mx-2"></v-divider>
            <v-card-text>
              <CategoryTagSelector
                v-model="value.tags"
                :return-object="false"
                :show-add="true"
                :tag-selector="true"
                :show-label="false"
              />
            </v-card-text>
          </v-card>
          <Nutrition v-model="value.nutrition" :edit="true" />
          <Assets v-model="value.assets" :edit="true" :slug="value.slug" />
          <ExtrasEditor :extras="value.extras" @save="saveExtras" />
        </v-col>

        <v-divider class="my-divider" :vertical="true"></v-divider>

        <v-col cols="12" sm="12" md="8" lg="8">
          <Instructions v-model="value.recipeInstructions" :edit="true" />
          <div class="d-flex row justify-end mt-2">
            <BulkAdd class="mr-2" @bulk-data="appendSteps" />
            <v-btn color="secondary" dark class="mr-4" @click="addStep">
              <v-icon>{{ $globals.icons.create }}</v-icon>
            </v-btn>
          </div>
          <Notes v-model="value.notes" :edit="true" />

          <v-text-field v-model="value.orgURL" class="mt-10" :label="$t('recipe.original-url')"></v-text-field>
        </v-col>
      </v-row>
    </v-card-text>
  </v-form>
</template>

<script>
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
import Rating from "@/components/Recipe/Parts/Rating";
const UPLOAD_EVENT = "upload";
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
    Rating,
  },
  mixins: [validators],
  props: {
    value: Object,
  },
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
          title: "",
          text: x,
        }))
      );
    },
    addStep() {
      this.value.recipeInstructions.push({ title: "", text: "" });
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
