<template>
  <v-container fluid>
    <!-- Dialog Object -->
    <BaseDialog
      ref="domDialog"
      width="650px"
      :icon="dialog.icon"
      :title="dialog.title"
      submit-text="Submit"
      @submit="dialog.callback"
    >
      <v-card-text v-if="dialog.mode == MODES.tag">
        <RecipeCategoryTagSelector v-model="toSetTags" :tag-selector="true" />
      </v-card-text>
      <v-card-text v-else-if="dialog.mode == MODES.category">
        <RecipeCategoryTagSelector v-model="toSetCategories" />
      </v-card-text>
      <v-card-text v-else-if="dialog.mode == MODES.delete">
        Are you sure you want to delete the following recipes?
        <ul class="pt-5">
          <li v-for="recipe in selected" :key="recipe.slug">{{ recipe.name }}</li>
        </ul>
      </v-card-text>
      <v-card-text v-else-if="dialog.mode == MODES.export"> TODO: Export Stuff Here </v-card-text>
    </BaseDialog>
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="125" max-width="125" :src="require('~/static/svgs/manage-recipes.svg')"></v-img>
      </template>
      <template #title> Recipe Data Management </template>
      Lorem ipsum dolor, sit amet consectetur adipisicing elit. Saepe quidem repudiandae consequatur laboriosam maxime
      perferendis nemo asperiores ipsum est, tenetur ratione dolorum sapiente recusandae
    </BasePageTitle>
    <v-card-actions>
      <v-menu offset-y bottom nudge-bottom="6" :close-on-content-click="false">
        <template #activator="{ on, attrs }">
          <v-btn color="accent" class="mr-1" dark v-bind="attrs" v-on="on">
            <v-icon left>
              {{ $globals.icons.cog }}
            </v-icon>
            Columns
          </v-btn>
        </template>
        <v-card>
          <v-card-title class="py-2">
            <div>Recipe Columns</div>
          </v-card-title>
          <v-divider class="mx-2"></v-divider>
          <v-card-text class="mt-n5">
            <v-checkbox
              v-for="(itemValue, key) in headers"
              :key="key"
              v-model="headers[key]"
              dense
              flat
              inset
              :label="headerLabels[key]"
              hide-details
            ></v-checkbox>
          </v-card-text>
        </v-card>
      </v-menu>
      <BaseOverflowButton
        :disabled="selected.length < 1"
        mode="event"
        color="info"
        :items="actions"
        @export-selected="openDialog(MODES.export)"
        @tag-selected="openDialog(MODES.tag)"
        @categorize-selected="openDialog(MODES.category)"
        @delete-selected="openDialog(MODES.delete)"
      >
      </BaseOverflowButton>

      <p v-if="selected.length > 0" class="text-caption my-auto ml-5">Selected: {{ selected.length }}</p>
    </v-card-actions>
    <RecipeDataTable v-model="selected" :recipes="allRecipes" :show-headers="headers" />
    <v-card-actions class="justify-end">
      <BaseButton color="info">
        <template #icon>
          {{ $globals.icons.database }}
        </template>
        Import
      </BaseButton>
      <BaseButton color="info">
        <template #icon>
          {{ $globals.icons.database }}
        </template>
        Export All
      </BaseButton>
    </v-card-actions>
  </v-container>
</template>
    
<script lang="ts">
import { defineComponent, reactive, ref, useContext } from "@nuxtjs/composition-api";
import RecipeDataTable from "~/components/Domain/Recipe/RecipeDataTable.vue";
import RecipeCategoryTagSelector from "~/components/Domain/Recipe/RecipeCategoryTagSelector.vue";
import { useApiSingleton } from "~/composables/use-api";
import { useRecipes, allRecipes } from "~/composables/use-recipes";
import { Recipe } from "~/types/api-types/recipe";

const MODES = {
  tag: "tag",
  category: "category",
  export: "export",
  delete: "delete",
};

export default defineComponent({
  components: { RecipeDataTable, RecipeCategoryTagSelector },
  scrollToTop: true,
  setup() {
    const { getAllRecipes, refreshRecipes } = useRecipes(true, true);

    // @ts-ignore
    const { $globals } = useContext();

    const selected = ref([]);

    function resetAll() {
      selected.value = [];
      toSetTags.value = [];
      toSetCategories.value = [];
    }

    const headers = reactive({
      id: false,
      owner: true,
      tags: true,
      categories: true,
      recipeYield: false,
      dateAdded: false,
    });

    const headerLabels = {
      id: "Id",
      owner: "Owner",
      tags: "Tags",
      categories: "Categories",
      recipeYield: "Recipe Yield",
      dateAdded: "Date Added",
    };

    const actions = [
      {
        icon: $globals.icons.database,
        text: "Export",
        value: 0,
        event: "export-selected",
      },
      {
        icon: $globals.icons.tags,
        text: "Tag",
        value: 1,
        event: "tag-selected",
      },
      {
        icon: $globals.icons.tags,
        text: "Categorize",
        value: 2,
        event: "categorize-selected",
      },
      {
        icon: $globals.icons.delete,
        text: "Delete",
        value: 3,
        event: "delete-selected",
      },
    ];

    const api = useApiSingleton();

    function exportSelected() {
      console.log("Export Selected");
    }

    const toSetTags = ref([]);

    async function tagSelected() {
      const recipes = selected.value.map((x: Recipe) => x.slug);
      await api.bulk.bulkTag({ recipes, tags: toSetTags.value });
      await refreshRecipes();
      resetAll();
    }

    const toSetCategories = ref([]);

    async function categorizeSelected() {
      const recipes = selected.value.map((x: Recipe) => x.slug);
      await api.bulk.bulkCategorize({ recipes, categories: toSetCategories.value });
      await refreshRecipes();
      resetAll();
    }

    async function deleteSelected() {
      const recipes = selected.value.map((x: Recipe) => x.slug);

      const { response, data } = await api.bulk.bulkDelete({ recipes });

      console.log(response, data);

      await refreshRecipes();
      resetAll();
    }

    // ============================================================
    // Dialog Management

    const domDialog = ref(null);

    const dialog = reactive({
      title: "Tag Recipes",
      mode: MODES.tag,
      tag: "",
      callback: () => {},
      icon: $globals.icons.tags,
    });

    function openDialog(mode: string) {
      const titles = {
        [MODES.tag]: "Tag Recipes",
        [MODES.category]: "Categorize Recipes",
        [MODES.export]: "Export Recipes",
        [MODES.delete]: "Delete Recipes",
      };

      const callbacks = {
        [MODES.tag]: tagSelected,
        [MODES.category]: categorizeSelected,
        [MODES.export]: exportSelected,
        [MODES.delete]: deleteSelected,
      };

      const icons = {
        [MODES.tag]: $globals.icons.tags,
        [MODES.category]: $globals.icons.tags,
        [MODES.export]: $globals.icons.database,
        [MODES.delete]: $globals.icons.delete,
      };

      dialog.mode = mode;
      dialog.title = titles[mode];
      dialog.callback = callbacks[mode];
      dialog.icon = icons[mode];
      // @ts-ignore
      domDialog.value.open();
    }

    return {
      toSetTags,
      toSetCategories,
      openDialog,
      domDialog,
      dialog,
      MODES,
      headers,
      headerLabels,
      exportSelected,
      tagSelected,
      categorizeSelected,
      deleteSelected,
      actions,
      selected,
      allRecipes,
      getAllRecipes,
    };
  },
  head() {
    return {
      title: "Recipe Data",
    };
  },
});
</script>