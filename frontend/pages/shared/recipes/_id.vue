<template>
  <v-container
    :class="{
      'pa-0': $vuetify.breakpoint.smAndDown,
    }"
  >
    <v-card v-if="skeleton" :color="`white ${false ? 'darken-2' : 'lighten-4'}`" class="pa-3">
      <v-skeleton-loader class="mx-auto" height="700px" type="card"></v-skeleton-loader>
    </v-card>
    <v-card v-else-if="recipe" class="d-print-none">
      <!-- Recipe Header -->
      <div class="d-flex justify-end flex-wrap align-stretch">
        <v-card v-if="!enableLandscape" width="50%" flat class="d-flex flex-column justify-center align-center">
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
                class="d-flex justify-center flex-wrap"
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
          :max-width="enableLandscape ? null : '50%'"
          :height="hideImage ? '50' : imageHeight"
          :src="recipeImage(recipe.slug, imageKey)"
          class="d-print-none"
          @error="hideImage = true"
        >
          <RecipeTimeCard
            v-if="enableLandscape"
            :class="true ? undefined : 'force-bottom'"
            :prep-time="recipe.prepTime"
            :total-time="recipe.totalTime"
            :perform-time="recipe.performTime"
          />
        </v-img>
      </div>
      <v-divider></v-divider>

      <!--  Editors  -->
      <div>
        <v-card-text
          :class="{
            'px-2': $vuetify.breakpoint.smAndDown,
          }"
        >
          <!-- Recipe Title Section -->
          <template v-if="!form && enableLandscape">
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
            <v-text-field v-model="recipe.recipeYield" dense :label="$t('recipe.servings')"> </v-text-field>
          </template>

          <div class="d-flex justify-space-between align-center pb-3">
            <v-tooltip v-if="!form" small top color="secondary darken-1">
              <template #activator="{ on, attrs }">
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
                  v-bind="attrs"
                  @click="scale = 1"
                  v-on="on"
                >
                  {{ scaledYield }}
                </v-btn>
              </template>
              <span> Reset Scale </span>
            </v-tooltip>

            <template v-if="!recipe.settings.disableAmount && !form">
              <v-btn color="secondary darken-1" class="mx-1" small @click="scale > 1 ? scale-- : null">
                <v-icon>
                  {{ $globals.icons.minus }}
                </v-icon>
              </v-btn>
              <v-btn color="secondary darken-1" small @click="scale++">
                <v-icon>
                  {{ $globals.icons.createAlt }}
                </v-icon>
              </v-btn>
            </template>
            <v-spacer></v-spacer>

            <RecipeRating
              v-if="enableLandscape"
              :key="recipe.slug"
              :value="recipe.rating"
              :name="recipe.name"
              :slug="recipe.slug"
            />
          </div>

          <v-row>
            <v-col cols="12" sm="12" md="4" lg="4">
              <RecipeIngredients
                v-if="!form"
                :value="recipe.recipeIngredient"
                :scale="scale"
                :disable-amount="recipe.settings.disableAmount"
              />

              <!-- Recipe Tools Display -->
              <div v-if="!form && recipe.tools && recipe.tools.length > 0">
                <h2 class="mb-2 mt-4">Required Tools</h2>
                <v-list-item v-for="(tool, index) in recipe.tools" :key="index" dense>
                  <v-checkbox
                    v-model="recipe.tools[index].onHand"
                    hide-details
                    class="pt-0 my-auto py-auto"
                    color="secondary"
                    @change="updateTool(recipe.tools[index])"
                  >
                  </v-checkbox>
                  <v-list-item-content>
                    {{ tool.name }}
                  </v-list-item-content>
                </v-list-item>
              </div>

              <div v-if="$vuetify.breakpoint.mdAndUp" class="mt-5">
                <!-- Recipe Categories -->
                <v-card v-if="recipe.recipeCategory.length > 0 || form" class="mt-2">
                  <v-card-title class="py-2">
                    {{ $t("recipe.categories") }}
                  </v-card-title>
                  <v-divider class="mx-2"></v-divider>
                  <v-card-text>
                    <RecipeChips :items="recipe.recipeCategory" />
                  </v-card-text>
                </v-card>

                <!-- Recipe Tags -->
                <v-card v-if="recipe.tags.length > 0 || form" class="mt-2">
                  <v-card-title class="py-2">
                    {{ $t("tag.tags") }}
                  </v-card-title>
                  <v-divider class="mx-2"></v-divider>
                  <v-card-text>
                    <RecipeChips :items="recipe.tags" :is-category="false" />
                  </v-card-text>
                </v-card>

                <RecipeNutrition
                  v-if="recipe.settings.showNutrition"
                  v-model="recipe.nutrition"
                  class="mt-10"
                  :edit="form"
                />
              </div>
            </v-col>
            <v-divider v-if="$vuetify.breakpoint.mdAndUp" class="my-divider" :vertical="true"></v-divider>

            <v-col cols="12" sm="12" md="8" lg="8">
              <RecipeInstructions
                v-model="recipe.recipeInstructions"
                :ingredients="recipe.recipeIngredient"
                :disable-amount="recipe.settings.disableAmount"
                :edit="form"
                public
              />

              <!-- TODO: Somehow fix duplicate code for mobile/desktop -->
              <div v-if="!$vuetify.breakpoint.mdAndUp" class="mt-5">
                <!-- Recipe Categories -->
                <v-card v-if="recipe.recipeCategory.length > 0 || form" class="mt-2">
                  <v-card-title class="py-2">
                    {{ $t("recipe.categories") }}
                  </v-card-title>
                  <v-divider class="mx-2"></v-divider>
                  <v-card-text>
                    <RecipeChips :items="recipe.recipeCategory" />
                  </v-card-text>
                </v-card>

                <!-- Recipe Tags -->
                <v-card v-if="recipe.tags.length > 0 || form" class="mt-2">
                  <v-card-title class="py-2">
                    {{ $t("tag.tags") }}
                  </v-card-title>
                  <v-divider class="mx-2"></v-divider>
                  <v-card-text>
                    <RecipeChips :items="recipe.tags" :is-category="false" />
                  </v-card-text>
                </v-card>

                <RecipeNutrition
                  v-if="recipe.settings.showNutrition"
                  v-model="recipe.nutrition"
                  class="mt-10"
                  :edit="form"
                />
              </div>

              <RecipeNotes v-model="recipe.notes" :edit="form" />
            </v-col>
          </v-row>

          <v-card-actions class="justify-end">
            <v-btn
              v-if="recipe.orgURL"
              dense
              small
              :hover="false"
              type="label"
              :ripple="false"
              elevation="0"
              :href="recipe.orgURL"
              color="secondary darken-1"
              target="_blank"
              class="rounded-sm mr-4"
            >
              {{ $t("recipe.original-url") }}
            </v-btn>
          </v-card-actions>
        </v-card-text>
      </div>
    </v-card>
    <RecipePrintView v-if="recipe" :recipe="recipe" />
  </v-container>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  useAsync,
  useContext,
  useMeta,
  useRoute,
} from "@nuxtjs/composition-api";
// @ts-ignore vue-markdown has no types
import VueMarkdown from "@adapttive/vue-markdown";
// import { useRecipeMeta } from "~/composables/recipes";
import { useStaticRoutes, useUserApi } from "~/composables/api";
import RecipeChips from "~/components/Domain/Recipe/RecipeChips.vue";
import RecipeIngredients from "~/components/Domain/Recipe/RecipeIngredients.vue";
import RecipeRating from "~/components/Domain/Recipe/RecipeRating.vue";
import RecipeTimeCard from "~/components/Domain/Recipe/RecipeTimeCard.vue";
import RecipeNutrition from "~/components/Domain/Recipe/RecipeNutrition.vue";
import RecipeInstructions from "~/components/Domain/Recipe/RecipeInstructions.vue";
import RecipeNotes from "~/components/Domain/Recipe/RecipeNotes.vue";
import RecipePrintView from "~/components/Domain/Recipe/RecipePrintView.vue";

export default defineComponent({
  components: {
    RecipeChips,
    RecipeIngredients,
    RecipeInstructions,
    RecipeNotes,
    RecipeNutrition,
    RecipePrintView,
    RecipeRating,
    RecipeTimeCard,
    VueMarkdown,
  },
  layout: "basic",
  setup() {
    const route = useRoute();
    const id = route.value.params.id;
    const api = useUserApi();

    const state = reactive({
      form: false,
      scale: 1,
      hideImage: false,
      imageKey: 1,
      loadFailed: false,
      skeleton: false,
      jsonEditor: false,
      jsonEditorOptions: {
        mode: "code",
        search: false,
        mainMenuBar: false,
      },
    });

    const { recipeImage } = useStaticRoutes();
    const { meta, title } = useMeta();

    const recipe = useAsync(async () => {
      const { data } = await api.recipes.getShared(id);
      if (data) {
        if (data && data !== undefined) {
          console.log("Computed Meta. RefKey=");
          const imageURL = data.id ? recipeImage(data.id) : undefined;
          title.value = data.name;

          meta.value = [
            { hid: "og:title", property: "og:title", content: data.name ?? "" },
            {
              hid: "og:desc",
              property: "og:description",
              content: data.description ?? "",
            },
            {
              hid: "og-image",
              property: "og:image",
              content: imageURL ?? "",
            },
            {
              hid: "twitter:title",
              property: "twitter:title",
              content: data.name ?? "",
            },
            {
              hid: "twitter:desc",
              property: "twitter:description",
              content: data.description ?? "",
            },
            { hid: "t-type", name: "twitter:card", content: "summary_large_image" },
          ];
        }
        return data;
      }
    });

    const { $vuetify } = useContext();

    const enableLandscape = computed(() => {
      const preferLandscape = recipe.value?.settings?.landscapeView;
      const smallScreen = !$vuetify.breakpoint.smAndUp;

      if (preferLandscape) {
        return true;
      } else if (smallScreen) {
        return true;
      }

      return false;
    });

    const scaledYield = computed(() => {
      const regMatchNum = /\d+/;
      const yieldString = recipe.value?.recipeYield;
      const num = yieldString?.match(regMatchNum);

      if (num && num?.length > 0) {
        const yieldAsInt = parseInt(num[0]);
        return yieldString?.replace(num[0], String(yieldAsInt * state.scale));
      }

      return recipe.value?.recipeYield;
    });

    return {
      ...toRefs(state),
      recipe,
      recipeImage,
      scaledYield,
      enableLandscape,
    };
  },
  head: {},
  computed: {
    imageHeight() {
      return this.$vuetify.breakpoint.xs ? "200" : "400";
    },
  },
});
</script>
