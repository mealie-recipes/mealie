<template>
  <v-container fluid>
    <!-- Export Purge Confirmation Dialog -->
    <BaseDialog
      v-model="purgeExportsDialog"
      :title="$t('data-pages.recipes.purge-exports')"
      color="error"
      :icon="$globals.icons.alertCircle"
      @confirm="purgeExports()"
    >
      <v-card-text> {{ $t('data-pages.recipes.are-you-sure-you-want-to-delete-all-export-data') }} </v-card-text>
    </BaseDialog>

    <!-- Base Dialog Object -->
    <BaseDialog
      ref="domDialog"
      v-model="dialog.state"
      width="650px"
      :icon="dialog.icon"
      :title="dialog.title"
      :submit-text="$t('general.submit')"
      @submit="dialog.callback"
    >
      <v-card-text v-if="dialog.mode == MODES.tag">
        <RecipeOrganizerSelector v-model="toSetTags" selector-type="tags" />
      </v-card-text>
      <v-card-text v-else-if="dialog.mode == MODES.category">
        <RecipeOrganizerSelector v-model="toSetCategories" selector-type="categories" />
      </v-card-text>
      <v-card-text v-else-if="dialog.mode == MODES.delete">
        <p class="h4">{{ $t('data-pages.recipes.confirm-delete-recipes') }}</p>
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
        <p class="h4">{{ $t('data-pages.recipes.the-following-recipes-selected-length-will-be-exported', [selected.length]) }}</p>
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
      <v-card-text v-else-if="dialog.mode == MODES.updateSettings" class="px-12">
        <p>{{ $t('data-pages.recipes.settings-chosen-explanation') }}</p>
        <div class="mx-auto">
          <RecipeSettingsSwitches v-model="recipeSettings" />
        </div>
        <p class="text-center mb-0">
          <i>{{ $tc('data-pages.recipes.selected-length-recipe-s-settings-will-be-updated', selected.length) }}</i>
        </p>
      </v-card-text>
      <v-card-text v-else-if="dialog.mode == MODES.changeOwner">
        <v-select
          v-model="selectedOwner"
          :items="allUsers"
          item-text="fullName"
          item-value="id"
          :label="$tc('general.owner')"
          hide-details
        >
          <template #prepend>
            <UserAvatar :user-id="selectedOwner" :tooltip="false" />
          </template>
        </v-select>
        <v-card-text v-if="selectedOwnerHousehold" class="d-flex" style="align-items: flex-end;">
          <v-icon>{{ $globals.icons.household }}</v-icon>
          <span class="pl-1">{{ selectedOwnerHousehold.name }}</span>
        </v-card-text>
      </v-card-text>
    </BaseDialog>
    <section>
      <!-- Recipe Data Table -->
      <BaseCardSectionTitle :icon="$globals.icons.primary" :title="$tc('data-pages.recipes.recipe-data')">
        {{ $t('data-pages.recipes.recipe-data-description') }}
      </BaseCardSectionTitle>
      <v-card-actions class="mt-n5 mb-1">
        <v-menu offset-y bottom nudge-bottom="6" :close-on-content-click="false">
          <template #activator="{ on, attrs }">
            <v-btn color="accent" class="mr-2" dark v-bind="attrs" v-on="on">
              <v-icon left>
                {{ $globals.icons.cog }}
              </v-icon>
              {{ $t('data-pages.columns') }}
            </v-btn>
          </template>
          <v-card>
            <v-card-title class="py-2">
              <div>{{ $t('data-pages.recipes.recipe-columns') }}</div>
            </v-card-title>
            <v-divider class="mx-2"></v-divider>
            <v-card-text class="mt-n5">
              <v-checkbox
                v-for="(_, key) in headers"
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
          @update-settings="openDialog(MODES.updateSettings)"
          @change-owner="openDialog(MODES.changeOwner)"
        >
        </BaseOverflowButton>

        <p v-if="selected.length > 0" class="text-caption my-auto ml-5">{{ $tc('general.selected-count', selected.length) }}</p>
      </v-card-actions>
      <v-card>
        <RecipeDataTable v-model="selected" :loading="loading" :recipes="allRecipes" :show-headers="headers" />
        <v-card-actions class="justify-end">
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
            {{ $t('general.export-all') }}
          </BaseButton>
        </v-card-actions>
      </v-card>
    </section>

    <section class="mt-10">
      <!-- Data Table -->
      <BaseCardSectionTitle :icon="$globals.icons.database" section :title="$tc('data-pages.recipes.data-exports')">
        {{ $t('data-pages.recipes.data-exports-description') }}
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
import { computed, defineComponent, reactive, ref, useContext, onMounted } from "@nuxtjs/composition-api";
import RecipeDataTable from "~/components/Domain/Recipe/RecipeDataTable.vue";
import RecipeOrganizerSelector from "~/components/Domain/Recipe/RecipeOrganizerSelector.vue";
import { useUserApi } from "~/composables/api";
import { useRecipes, allRecipes } from "~/composables/recipes";
import { Recipe, RecipeSettings } from "~/lib/api/types/recipe";
import GroupExportData from "~/components/Domain/Group/GroupExportData.vue";
import { GroupDataExport } from "~/lib/api/types/group";
import { MenuItem } from "~/components/global/BaseOverflowButton.vue";
import RecipeSettingsSwitches from "~/components/Domain/Recipe/RecipeSettingsSwitches.vue";
import { useUserStore } from "~/composables/store/use-user-store";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";
import { useHouseholdStore } from "~/composables/store/use-household-store";

enum MODES {
  tag = "tag",
  category = "category",
  export = "export",
  delete = "delete",
  updateSettings = "updateSettings",
  changeOwner = "changeOwner",
}

export default defineComponent({
  components: { RecipeDataTable, RecipeOrganizerSelector, GroupExportData, RecipeSettingsSwitches, UserAvatar },
  scrollToTop: true,
  setup() {
    const { $auth, $globals, i18n } = useContext();
    const { getAllRecipes, refreshRecipes } = useRecipes(true, true, false, `householdId=${$auth.user?.householdId || ""}`);
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
      recipeServings: false,
      recipeYieldQuantity: false,
      recipeYield: false,
      dateAdded: false,
    });

    const headerLabels = {
      id: i18n.t("general.id"),
      owner: i18n.t("general.owner"),
      tags: i18n.t("tag.tags"),
      categories: i18n.t("recipe.categories"),
      tools: i18n.t("tool.tools"),
      recipeServings: i18n.t("recipe.recipe-servings"),
      recipeYieldQuantity: i18n.t("recipe.recipe-yield"),
      recipeYield: i18n.t("recipe.recipe-yield-text"),
      dateAdded: i18n.t("general.date-added"),
    };

    const actions: MenuItem[] = [
      {
        icon: $globals.icons.database,
        text: i18n.tc("export.export"),
        event: "export-selected",
      },
      {
        icon: $globals.icons.tags,
        text: i18n.tc("data-pages.recipes.tag"),
        event: "tag-selected",
      },
      {
        icon: $globals.icons.categories,
        text: i18n.tc("data-pages.recipes.categorize"),
        event: "categorize-selected",
      },
      {
        icon: $globals.icons.cog,
        text: i18n.tc("data-pages.recipes.update-settings"),
        event: "update-settings",
      },
      {
        icon: $globals.icons.user,
        text: i18n.tc("general.change-owner"),
        event: "change-owner",
      },
      {
        icon: $globals.icons.delete,
        text: i18n.tc("general.delete"),
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

      await api.bulk.bulkDelete({ recipes });

      await refreshRecipes();
      resetAll();
    }

    const recipeSettings = reactive<RecipeSettings>({
      public: false,
      showNutrition: false,
      showAssets: false,
      landscapeView: false,
      disableComments: false,
      disableAmount: false,
      locked: false,
    });

    async function updateSettings() {
      loading.value = true;

      const recipes = selected.value.map((x: Recipe) => x.slug ?? "");

      await api.bulk.bulkSetSettings({ recipes, settings: recipeSettings });

      await refreshRecipes();
      resetAll();
    }

    async function changeOwner() {
      if(!selected.value.length || !selectedOwner.value) {
        return;
      }

      selected.value.forEach((r) => {
        r.userId = selectedOwner.value;
      });

      loading.value = true;
      await api.recipes.patchMany(selected.value);

      await refreshRecipes();
      resetAll();
    }

    // ============================================================
    // Dialog Management

    const dialog = reactive({
      state: false,
      title: i18n.t("data-pages.recipes.tag-recipes"),
      mode: MODES.tag,
      tag: "",
      callback: () => {
        // Stub function to be overwritten
        return Promise.resolve();
      },
      icon: $globals.icons.tags,
    });

    function openDialog(mode: MODES) {
      const titles: Record<MODES, string> = {
        [MODES.tag]: i18n.tc("data-pages.recipes.tag-recipes"),
        [MODES.category]: i18n.tc("data-pages.recipes.categorize-recipes"),
        [MODES.export]: i18n.tc("data-pages.recipes.export-recipes"),
        [MODES.delete]: i18n.tc("data-pages.recipes.delete-recipes"),
        [MODES.updateSettings]: i18n.tc("data-pages.recipes.update-settings"),
        [MODES.changeOwner]: i18n.tc("general.change-owner"),
      };

      const callbacks: Record<MODES, () => Promise<void>> = {
        [MODES.tag]: tagSelected,
        [MODES.category]: categorizeSelected,
        [MODES.export]: exportSelected,
        [MODES.delete]: deleteSelected,
        [MODES.updateSettings]: updateSettings,
        [MODES.changeOwner]: changeOwner,
      };

      const icons: Record<MODES, string> = {
        [MODES.tag]: $globals.icons.tags,
        [MODES.category]: $globals.icons.categories,
        [MODES.export]: $globals.icons.database,
        [MODES.delete]: $globals.icons.delete,
        [MODES.updateSettings]: $globals.icons.cog,
        [MODES.changeOwner]: $globals.icons.user,
      };

      dialog.mode = mode;
      dialog.title = titles[mode];
      dialog.callback = callbacks[mode];
      dialog.icon = icons[mode];
      dialog.state = true;
    }

    const { store: allUsers } = useUserStore();
    const { store: households } = useHouseholdStore();
    const selectedOwner = ref("");
    const selectedOwnerHousehold = computed(() => {
      if(!selectedOwner.value) {
        return null;
      }

      const owner = allUsers.value.find((u) => u.id === selectedOwner.value);
      if (!owner) {
        return null;
      };

      return households.value.find((h) => h.id === owner.householdId);
    });

    return {
      recipeSettings,
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
      allUsers,
      selectedOwner,
      selectedOwnerHousehold,
    };
  },
  head() {
    return {
      title: this.$tc("data-pages.recipes.recipe-data"),
    };
  },
});
</script>
