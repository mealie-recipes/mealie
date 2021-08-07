<template>
  <v-container>
    <v-card v-if="skeleton" :color="`white ${false ? 'darken-2' : 'lighten-4'}`" class="pa-3">
      <v-skeleton-loader class="mx-auto" height="700px" type="card"></v-skeleton-loader>
    </v-card>
    <v-card v-else-if="recipe">
      <div class="d-flex justify-end flex-wrap align-stretch">
        <v-card
          v-if="!recipe.settings.landscapeView"
          width="50%"
          flat
          class="d-flex flex-column justify-center align-center"
        >
          <v-card-text>
            <v-card-title class="headline pa-0 flex-column align-center">
              {{ recipe.name }}
              <RecipeRating :key="recipe.slug" :value="recipe.rating" :name="recipe.name" :slug="recipe.slug" />
            </v-card-title>
            <v-divider class="my-2"></v-divider>
            <VueMarkdown :source="recipe.description"> </VueMarkdown>
            <v-divider></v-divider>
            <div class="d-flex justify-center mt-5">
              <RecipeTimeCard
                :class="true ? undefined : 'force-bottom'"
                :prep-time="recipe.prepTime"
                :total-time="recipe.totalTime"
                :perform-time="recipe.performTime"
              />
            </div>
          </v-card-text>
        </v-card>
        <v-img
          :key="imageKey"
          :max-width="recipe.settings.landscapeView ? null : '50%'"
          :height="hideImage ? '50' : imageHeight"
          :src="api.recipes.recipeImage(recipe.slug, imageKey)"
          class="d-print-none"
          @error="hideImage = true"
        >
          <RecipeTimeCard
            v-if="recipe.settings.landscapeView"
            :class="true ? undefined : 'force-bottom'"
            :prep-time="recipe.prepTime"
            :total-time="recipe.totalTime"
            :perform-time="recipe.performTime"
          />
        </v-img>
      </div>
      <v-divider></v-divider>
      <RecipeActionMenu
        v-model="form"
        :slug="recipe.slug"
        :name="recipe.name"
        :logged-in="$auth.loggedIn"
        :open="form"
        class="ml-auto"
        @close="form = false"
        @json="jsonEditor = !jsonEditor"
        @edit="
          jsonEditor = false;
          form = true;
        "
        @save="updateRecipe(recipe.slug, recipe)"
        @delete="deleteRecipe(recipe.slug)"
      />

      <div>
        <v-card-text>
          <div v-if="form" class="d-flex justify-start align-center">
            <RecipeImageUploadBtn class="my-1" :slug="recipe.slug" @upload="uploadImage" @refresh="imageKey++" />
            <RecipeSettingsMenu class="my-1 mx-1" :value="recipe.settings" @upload="uploadImage" />
          </div>
          <!-- Recipe Title Section -->
          <template v-if="!form && recipe.settings.landscapeView">
            <v-card-title class="pa-0 ma-0 headline">
              {{ recipe.name }}
            </v-card-title>
            <VueMarkdown :source="recipe.description"> </VueMarkdown>
          </template>

          <template v-else-if="form">
            <v-text-field
              v-model="recipe.name"
              class="my-3"
              :label="$t('recipe.recipe-name')"
              :rules="[validators.required]"
            >
            </v-text-field>

            <div class="d-flex flex-wrap">
              <v-text-field v-model="recipe.totalTime" class="mx-2" :label="$t('recipe.total-time')"></v-text-field>
              <v-text-field v-model="recipe.prepTime" class="mx-2" :label="$t('recipe.prep-time')"></v-text-field>
              <v-text-field v-model="recipe.performTime" class="mx-2" :label="$t('recipe.perform-time')"></v-text-field>
            </div>

            <v-textarea v-model="recipe.description" auto-grow min-height="100" :label="$t('recipe.description')">
            </v-textarea>
          </template>

          <div class="d-flex justify-space-between align-center pb-3">
            <v-btn
              v-if="recipe.recipeYield"
              dense
              small
              :hover="false"
              type="label"
              :ripple="false"
              elevation="0"
              color="secondary darken-1"
              class="rounded-sm static"
            >
              {{ recipe.recipeYield }}
            </v-btn>
            <RecipeRating
              v-if="recipe.settings.landscapeView"
              :key="recipe.slug"
              :value="recipe.rating"
              :name="recipe.name"
              :slug="recipe.slug"
            />
          </div>
          <v-row>
            <v-col cols="12" sm="12" md="4" lg="4">
              <RecipeIngredients :value="recipe.recipeIngredient" :edit="form" />
              <div v-if="$vuetify.breakpoint.mdAndUp">
                <v-card v-if="recipe.recipeCategory.length > 0" class="mt-2">
                  <v-card-title class="py-2">
                    {{ $t("recipe.categories") }}
                  </v-card-title>
                  <v-divider class="mx-2"></v-divider>
                  <v-card-text>
                    <RecipeChips :items="recipe.recipeCategory" />
                  </v-card-text>
                </v-card>
                <v-card v-if="recipe.tags.length > 0" class="mt-2">
                  <v-card-title class="py-2">
                    {{ $t("tag.tags") }}
                  </v-card-title>
                  <v-divider class="mx-2"></v-divider>
                  <v-card-text>
                    <RecipeChips :items="recipe.tags" :is-category="false" />
                  </v-card-text>
                </v-card>

                <RecipeNutrition v-if="true || form" v-model="recipe.nutrition" class="mt-10" :edit="form" />
                <RecipeAssets
                  v-if="recipe.settings.showAssets || form"
                  v-model="recipe.assets"
                  :edit="form"
                  :slug="recipe.slug"
                />
              </div>
            </v-col>
            <v-divider v-if="$vuetify.breakpoint.mdAndUp" class="my-divider" :vertical="true"></v-divider>

            <v-col cols="12" sm="12" md="8" lg="8">
              <RecipeInstructions v-model="recipe.recipeInstructions" :edit="form" />
              <RecipeNotes v-model="recipe.notes" :edit="form" />
            </v-col>
          </v-row>
        </v-card-text>
      </div>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, ref, useMeta, useRoute, useRouter } from "@nuxtjs/composition-api";
// @ts-ignore
import VueMarkdown from "@adapttive/vue-markdown";
import { useApiSingleton } from "~/composables/use-api";
import { validators } from "~/composables/use-validators";
import { useRecipeContext } from "~/composables/use-recipe-context";
import RecipeActionMenu from "~/components/Domain/Recipe/RecipeActionMenu.vue";
import RecipeChips from "~/components/Domain/Recipe/RecipeChips.vue";
import RecipeIngredients from "~/components/Domain/Recipe/RecipeIngredients.vue";
import RecipeRating from "~/components/Domain/Recipe/RecipeRating.vue";
import RecipeTimeCard from "~/components/Domain/Recipe/RecipeTimeCard.vue";
import RecipeAssets from "~/components/Domain/Recipe/RecipeAssets.vue";
import RecipeNutrition from "~/components/Domain/Recipe/RecipeNutrition.vue";
import RecipeInstructions from "~/components/Domain/Recipe/RecipeInstructions.vue";
import RecipeNotes from "~/components/Domain/Recipe/RecipeNotes.vue";
import RecipeImageUploadBtn from "~/components/Domain/Recipe/RecipeImageUploadBtn.vue";
import RecipeSettingsMenu from "~/components/Domain/Recipe/RecipeSettingsMenu.vue";
import { Recipe } from "~/types/api-types/admin";

export default defineComponent({
  components: {
    RecipeActionMenu,
    RecipeAssets,
    RecipeChips,
    RecipeIngredients,
    RecipeInstructions,
    RecipeNotes,
    RecipeNutrition,
    RecipeRating,
    RecipeTimeCard,
    RecipeImageUploadBtn,
    RecipeSettingsMenu,
    VueMarkdown,
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const slug = route.value.params.slug;
    const api = useApiSingleton();
    const imageKey = ref(1);

    const { getBySlug, loading } = useRecipeContext();

    const recipe = getBySlug(slug);

    const form = ref<boolean>(false);

    useMeta(() => ({ title: recipe?.value?.name || "Recipe" }));

    async function updateRecipe(slug: string, recipe: Recipe) {
      const { data } = await api.recipes.updateOne(slug, recipe);
      form.value = false;
      if (data?.slug) {
        router.push("/recipe/" + data.slug);
      }
    }

    async function deleteRecipe(slug: string) {
      const { data } = await api.recipes.deleteOne(slug);
      if (data?.slug) {
        router.push("/");
      }
    }

    async function uploadImage(fileObject: File) {
      if (!recipe.value) {
        return;
      }
      const newVersion = await api.recipes.updateImage(recipe.value.slug, fileObject);
      if (newVersion?.data?.version) {
        recipe.value.image = newVersion.data.version;
      }
      imageKey.value++;
    }

    return {
      imageKey,
      recipe,
      api,
      form,
      loading,
      deleteRecipe,
      updateRecipe,
      uploadImage,
      validators,
    };
  },
  data() {
    return {
      hideImage: false,
      loadFailed: false,
      skeleton: false,
      jsonEditor: false,
      jsonEditorOptions: {
        mode: "code",
        search: false,
        mainMenuBar: false,
      },
    };
  },
  head: {},
  computed: {
    imageHeight() {
      // @ts-ignore
      return this.$vuetify.breakpoint.xs ? "200" : "400";
    },
  },
  methods: {
    printPage() {
      window.print();
    },
  },
});
</script>

<style scoped></style>
