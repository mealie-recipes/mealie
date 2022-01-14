<template>
  <v-container fluid>
    <!-- Export Purge Confirmation Dialog -->
    <BaseDialog
      v-model="purgeExportsDialog"
      title="Purge Exports"
      color="error"
      :icon="$globals.icons.alertCircle"
      @confirm="purgeExports()"
    >
      <v-card-text> Are you sure you want to delete all export data? </v-card-text>
    </BaseDialog>

    <!-- Base Dialog Object -->
    <BaseDialog
      ref="domDialog"
      v-model="dialog.state"
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
        <p class="h4">Are you sure you want to delete the following recipes? This action cannot be undone.</p>
        <v-card outlined>
          <v-virtual-scroll height="400" item-height="25" :items="selected">
            <template #default="{ item }">
              <v-list-item class="pb-2">
                <v-list-item-content>
                  <v-list-item-title>{{ item.name }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </template>
          </v-virtual-scroll>
        </v-card>
      </v-card-text>
      <v-card-text v-else-if="dialog.mode == MODES.export">
        <p class="h4">The following recipes ({{ selected.length }}) will be exported.</p>
        <v-card outlined>
          <v-virtual-scroll height="400" item-height="25" :items="selected">
            <template #default="{ item }">
              <v-list-item class="pb-2">
                <v-list-item-content>
                  <v-list-item-title>{{ item.name }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </template>
          </v-virtual-scroll>
        </v-card>
      </v-card-text>
    </BaseDialog>
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="125" max-width="125" :src="require('~/static/svgs/manage-recipes.svg')"></v-img>
      </template>
      <template #title> Data Management </template>
    </BasePageTitle>

    <section>
      <!-- Recipe Data Table -->
      <BaseCardSectionTitle :icon="$globals.icons.primary" section title="Recipe Data">
        Use this section to manage the data associated with your recipes. You can perform several bulk actions on your
        recipes including exporting, deleting, tagging, and assigning categories.
      </BaseCardSectionTitle>
      <v-card-actions class="mt-n5 mb-1">
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
      <v-card>
        <RecipeDataTable v-model="selected" :loading="loading" :recipes="allRecipes" :show-headers="headers" />
        <v-card-actions class="justify-end">
          <BaseButton color="info">
            <template #icon>
              {{ $globals.icons.database }}
            </template>
            Import
          </BaseButton>
          <BaseButton
            color="info"
            @click="
              selectAll();
              openDialog(MODES.export);
            "
          >
            <template #icon>
              {{ $globals.icons.database }}
            </template>
            Export All
          </BaseButton>
        </v-card-actions>
      </v-card>
    </section>

    <section class="mt-10">
      <!-- Downloads Data Table -->
      <BaseCardSectionTitle :icon="$globals.icons.database" section title="Data Exports">
        This section provides links to available exports that are ready to download. These exports do expire, so be sure
        to grab them while they're still available.
      </BaseCardSectionTitle>
      <v-card-actions class="mt-n5 mb-1">
        <BaseButton delete @click="purgeExportsDialog = true"> </BaseButton>
      </v-card-actions>
      <v-card>
        <GroupExportData :exports="groupExports" />
      </v-card>
    </section>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, useContext, onMounted } from "@nuxtjs/composition-api";
import RecipeDataTable from "~/components/Domain/Recipe/RecipeDataTable.vue";
import RecipeCategoryTagSelector from "~/components/Domain/Recipe/RecipeCategoryTagSelector.vue";
import { useUserApi } from "~/composables/api";
import { useRecipes, allRecipes } from "~/composables/recipes";
import { Recipe } from "~/types/api-types/recipe";
import GroupExportData from "~/components/Domain/Group/GroupExportData.vue";
import { GroupDataExport } from "~/api/class-interfaces/recipe-bulk-actions";
import { MenuItem } from "~/components/global/BaseOverflowButton.vue";

const MODES = {
  tag: "tag",
  category: "category",
  export: "export",
  delete: "delete",
};

export default defineComponent({
  components: { RecipeDataTable, RecipeCategoryTagSelector, GroupExportData },
  scrollToTop: true,
  setup() {
    const { getAllRecipes, refreshRecipes } = useRecipes(true, true);

    const { $globals } = useContext();

    const selected = ref<Recipe[]>([]);

    function resetAll() {
      selected.value = [];
      toSetTags.value = [];
      toSetCategories.value = [];
      loading.value = false;
    }

    const headers = reactive({
      id: false,
      owner: false,
      tags: true,
      tools: true,
      categories: true,
      recipeYield: false,
      dateAdded: false,
    });

    const headerLabels = {
      id: "Id",
      owner: "Owner",
      tags: "Tags",
      categories: "Categories",
      tools: "Tools",
      recipeYield: "Recipe Yield",
      dateAdded: "Date Added",
    };

    const actions: MenuItem[] = [
      {
        icon: $globals.icons.database,
        text: "Export",
        event: "export-selected",
      },
      {
        icon: $globals.icons.tags,
        text: "Tag",
        event: "tag-selected",
      },
      {
        icon: $globals.icons.tags,
        text: "Categorize",
        event: "categorize-selected",
      },
      {
        icon: $globals.icons.delete,
        text: "Delete",
        event: "delete-selected",
      },
    ];

    const api = useUserApi();
    const loading = ref(false);

    // ===============================================================
    // Group Exports

    const purgeExportsDialog = ref(false);

    async function purgeExports() {
      await api.bulk.purgeExports();
      refreshExports();
    }

    const groupExports = ref<GroupDataExport[]>([]);

    async function refreshExports() {
      const { data } = await api.bulk.fetchExports();

      if (data) {
        groupExports.value = data;
      }
    }

    onMounted(async () => {
      await refreshExports();
    });
    // ===============================================================
    // All Recipes

    function selectAll() {
      selected.value = allRecipes.value;
    }

    async function exportSelected() {
      loading.value = true;
      const { data } = await api.bulk.bulkExport({
        recipes: selected.value.map((x: Recipe) => x.slug ?? ""),
        exportType: "json",
      });

      if (data) {
        console.log(data);
      }

      resetAll();
      refreshExports();
    }

    const toSetTags = ref([]);

    async function tagSelected() {
      loading.value = true;

      const recipes = selected.value.map((x: Recipe) => x.slug ?? "");
      await api.bulk.bulkTag({ recipes, tags: toSetTags.value });
      await refreshRecipes();
      resetAll();
    }

    const toSetCategories = ref([]);

    async function categorizeSelected() {
      loading.value = true;

      const recipes = selected.value.map((x: Recipe) => x.slug ?? "");
      await api.bulk.bulkCategorize({ recipes, categories: toSetCategories.value });
      await refreshRecipes();
      resetAll();
    }

    async function deleteSelected() {
      loading.value = true;

      const recipes = selected.value.map((x: Recipe) => x.slug ?? "");

      const { response, data } = await api.bulk.bulkDelete({ recipes });

      console.log(response, data);

      await refreshRecipes();
      resetAll();
    }

    // ============================================================
    // Dialog Management

    const dialog = reactive({
      state: false,
      title: "Tag Recipes",
      mode: MODES.tag,
      tag: "",
      // eslint-disable-next-line @typescript-eslint/no-empty-function
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
      dialog.state = true;
    }

    return {
      selectAll,
      loading,
      actions,
      allRecipes,
      categorizeSelected,
      deleteSelected,
      dialog,
      exportSelected,
      getAllRecipes,
      headerLabels,
      headers,
      MODES,
      openDialog,
      selected,
      tagSelected,
      toSetCategories,
      toSetTags,
      groupExports,
      purgeExportsDialog,
      purgeExports,
    };
  },
  head() {
    return {
      title: "Recipe Data",
    };
  },
});
</script>
