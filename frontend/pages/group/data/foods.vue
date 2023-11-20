<template>
  <div>
    <!-- Merge Dialog -->
    <BaseDialog v-model="mergeDialog" :icon="$globals.icons.foods" :title="$t('data-pages.foods.combine-food')" @confirm="mergeFoods">
      <v-card-text>
        <div>
          {{ $t("data-pages.foods.merge-dialog-text") }}
        </div>
        <v-autocomplete v-model="fromFood" return-object :items="foods" item-text="name" :label="$t('data-pages.foods.source-food')" />
        <v-autocomplete v-model="toFood" return-object :items="foods" item-text="name" :label="$t('data-pages.foods.target-food')" />

        <template v-if="canMerge && fromFood && toFood">
          <div class="text-center">
            {{ $t("data-pages.foods.merge-food-example", { food1: fromFood.name, food2: toFood.name }) }}
          </div>
        </template>
      </v-card-text>
    </BaseDialog>

    <!-- Seed Dialog-->
    <BaseDialog
      v-model="seedDialog"
      :icon="$globals.icons.foods"
      :title="$tc('data-pages.seed-data')"
      @confirm="seedDatabase"
    >
      <v-card-text>
        <div class="pb-2">
          {{ $t("data-pages.foods.seed-dialog-text") }}
        </div>
        <v-autocomplete
          v-model="locale"
          :items="locales"
          item-text="name"
          :label="$t('data-pages.select-language')"
          class="my-3"
          hide-details
          outlined
          offset
        >
          <template #item="{ item }">
            <v-list-item-content>
              <v-list-item-title> {{ item.name }} </v-list-item-title>
              <v-list-item-subtitle>
                {{ item.progress }}% {{ $tc("language-dialog.translated") }}
              </v-list-item-subtitle>
            </v-list-item-content>
          </template>
        </v-autocomplete>

        <v-alert v-if="foods && foods.length > 0" type="error" class="mb-0 text-body-2">
          {{ $t("data-pages.foods.seed-dialog-warning") }}
        </v-alert>
      </v-card-text>
    </BaseDialog>

    <!-- Create Dialog -->
    <BaseDialog
      v-model="createDialog"
      :icon="$globals.icons.foods"
      :title="$t('data-pages.foods.create-food')"
      :submit-icon="$globals.icons.save"
      :submit-text="$tc('general.save')"
      @submit="createFood"
    >
      <v-card-text>
        <v-form ref="domNewFoodForm">
          <v-text-field
            v-model="createTarget.name"
            autofocus
            :label="$t('general.name')"
            :hint="$t('data-pages.foods.example-food-singular')"
            :rules="[validators.required]"
          ></v-text-field>
          <v-text-field
            v-model="createTarget.pluralName"
            :label="$t('general.plural-name')"
            :hint="$t('data-pages.foods.example-food-plural')"
          ></v-text-field>
          <v-text-field v-model="createTarget.description" :label="$t('recipe.description')"></v-text-field>
          <v-autocomplete
            v-model="createTarget.labelId"
            clearable
            :items="allLabels"
            item-value="id"
            item-text="name"
            :label="$t('data-pages.foods.food-label')"
          >
          </v-autocomplete>
        </v-form> </v-card-text
    ></BaseDialog>

    <!-- Alias Sub-Dialog -->
    <RecipeDataAliasManagerDialog
      v-if="editTarget"
      :value="aliasManagerDialog"
      :data="editTarget"
      @submit="updateFoodAlias"
      @cancel="aliasManagerDialog = false"
    />

    <!-- Edit Dialog -->
    <BaseDialog
      v-model="editDialog"
      :icon="$globals.icons.foods"
      :title="$t('data-pages.foods.edit-food')"
      :submit-icon="$globals.icons.save"
      :submit-text="$tc('general.save')"
      @submit="editSaveFood"
    >
      <v-card-text v-if="editTarget">
        <v-form ref="domEditFoodForm">
          <v-text-field
            v-model="editTarget.name"
            :label="$t('general.name')"
            :hint="$t('data-pages.foods.example-food-singular')"
            :rules="[validators.required]"
          ></v-text-field>
          <v-text-field
            v-model="editTarget.pluralName"
            :label="$t('general.plural-name')"
            :hint="$t('data-pages.foods.example-food-plural')"
          ></v-text-field>
          <v-text-field
            v-model="editTarget.description"
            :label="$t('recipe.description')"
          ></v-text-field>
          <v-autocomplete
            v-model="editTarget.labelId"
            clearable
            :items="allLabels"
            item-value="id"
            item-text="name"
            :label="$t('data-pages.foods.food-label')"
          >
          </v-autocomplete>
        </v-form>
      </v-card-text>
      <template #custom-card-action>
        <BaseButton edit @click="aliasManagerEventHandler">{{ $t('data-pages.manage-aliases') }}</BaseButton>
      </template>
    </BaseDialog>

    <!-- Delete Dialog -->
    <BaseDialog
      v-model="deleteDialog"
      :title="$tc('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      @confirm="deleteFood"
    >
      <v-card-text>
        <div class="mb-4">
          {{ $t("general.confirm-delete-generic") }}
        </div>
        <p v-if="deleteTarget" class="ml-4">{{ deleteTarget.name }}</p>
      </v-card-text>
    </BaseDialog>

    <!-- Recipe Data Table -->
    <BaseCardSectionTitle :icon="$globals.icons.foods" section :title="$tc('data-pages.foods.food-data')"> </BaseCardSectionTitle>
    <CrudTable
      :table-config="tableConfig"
      :headers.sync="tableHeaders"
      :data="foods || []"
      :bulk-actions="[]"
      @delete-one="deleteEventHandler"
      @edit-one="editEventHandler"
      @create-one="createEventHandler"
    >
      <template #button-row>
        <BaseButton create @click="createDialog = true" />
        <BaseButton @click="mergeDialog = true">
          <template #icon> {{ $globals.icons.foods }} </template>
          {{ $t('data-pages.combine') }}
        </BaseButton>
      </template>
      <template #item.label="{ item }">
        <MultiPurposeLabel v-if="item.label" :label="item.label">
          {{ item.label.name }}
        </MultiPurposeLabel>
      </template>
      <template #button-bottom>
        <BaseButton @click="seedDialog = true">
          <template #icon> {{ $globals.icons.database }} </template>
          {{ $t('data-pages.seed') }}
        </BaseButton>
      </template>
    </CrudTable>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref, computed, useContext } from "@nuxtjs/composition-api";
import type { LocaleObject } from "@nuxtjs/i18n";
import RecipeDataAliasManagerDialog from "~/components/Domain/Recipe/RecipeDataAliasManagerDialog.vue";
import { validators } from "~/composables/use-validators";
import { useUserApi } from "~/composables/api";
import { CreateIngredientFood, IngredientFood, IngredientFoodAlias } from "~/lib/api/types/recipe";
import MultiPurposeLabel from "~/components/Domain/ShoppingList/MultiPurposeLabel.vue";
import { useLocales } from "~/composables/use-locales";
import { useFoodStore, useLabelStore } from "~/composables/store";
import { VForm } from "~/types/vuetify";

export default defineComponent({

  components: { MultiPurposeLabel, RecipeDataAliasManagerDialog },
  setup() {
    const userApi = useUserApi();
    const { i18n } = useContext();
    const tableConfig = {
      hideColumns: true,
      canExport: true,
    };
    const tableHeaders = [
      {
        text: i18n.tc("general.id"),
        value: "id",
        show: false,
      },
      {
        text: i18n.tc("general.name"),
        value: "name",
        show: true,
      },
      {
        text: i18n.tc("general.plural-name"),
        value: "pluralName",
        show: true,
      },
      {
        text: i18n.tc("recipe.description"),
        value: "description",
        show: true,
      },
      {
        text: i18n.tc("shopping-list.label"),
        value: "label",
        show: true,
      },
    ];

    const foodStore = useFoodStore();

    // ===============================================================
    // Food Creator

    const domNewFoodForm = ref<VForm>();
    const createDialog = ref(false);
    const createTarget = ref<CreateIngredientFood>({
      name: "",
    });

    function createEventHandler() {
      createDialog.value = true;
    }

    async function createFood() {
      if (!createTarget.value || !createTarget.value.name) {
        return;
      }

      // @ts-expect-error the createOne function erroneously expects an id because it uses the IngredientFood type
      await foodStore.actions.createOne(createTarget.value);
      createDialog.value = false;

      domNewFoodForm.value?.reset();
      createTarget.value = {
        name: "",
      };
    }

    // ===============================================================
    // Food Editor

    const editDialog = ref(false);
    const editTarget = ref<IngredientFood | null>(null);

    function editEventHandler(item: IngredientFood) {
      editTarget.value = item;
      editDialog.value = true;
    }

    async function editSaveFood() {
      if (!editTarget.value) {
        return;
      }

      await foodStore.actions.updateOne(editTarget.value);
      editDialog.value = false;
    }

    // ===============================================================
    // Food Delete

    const deleteDialog = ref(false);
    const deleteTarget = ref<IngredientFood | null>(null);
    function deleteEventHandler(item: IngredientFood) {
      deleteTarget.value = item;
      deleteDialog.value = true;
    }
    async function deleteFood() {
      if (!deleteTarget.value) {
        return;
      }

      await foodStore.actions.deleteOne(deleteTarget.value.id);
      deleteDialog.value = false;
    }

    // ============================================================
    // Alias Manager

    const aliasManagerDialog = ref(false);
    function aliasManagerEventHandler() {
      aliasManagerDialog.value = true;
    }

    function updateFoodAlias(newAliases: IngredientFoodAlias[]) {
      if (!editTarget.value) {
        return;
      }
      editTarget.value.aliases = newAliases;
      aliasManagerDialog.value = false;
    }

    // ============================================================
    // Merge Foods

    const mergeDialog = ref(false);
    const fromFood = ref<IngredientFood | null>(null);
    const toFood = ref<IngredientFood | null>(null);

    const canMerge = computed(() => {
      return fromFood.value && toFood.value && fromFood.value.id !== toFood.value.id;
    });

    async function mergeFoods() {
      if (!canMerge.value || !fromFood.value || !toFood.value) {
        return;
      }

      const { data } = await userApi.foods.merge(fromFood.value.id, toFood.value.id);

      if (data) {
        foodStore.actions.refresh();
      }
    }

    // ============================================================
    // Labels

    const { labels: allLabels } = useLabelStore();

    // ============================================================
    // Seed

    const seedDialog = ref(false);
    const locale = ref("");

    const { locales: LOCALES, locale: currentLocale } = useLocales();

    onMounted(() => {
      locale.value = currentLocale.value;
    });

    const locales = LOCALES.filter((locale) =>
      (i18n.locales as LocaleObject[]).map((i18nLocale) => i18nLocale.code).includes(locale.value)
    );

    async function seedDatabase() {
      const { data } = await userApi.seeders.foods({ locale: locale.value });

      if (data) {
        foodStore.actions.refresh();
      }
    }

    return {
      tableConfig,
      tableHeaders,
      foods: foodStore.foods,
      allLabels,
      validators,
      // Create
      createDialog,
      domNewFoodForm,
      createEventHandler,
      createFood,
      createTarget,
      // Edit
      editDialog,
      editEventHandler,
      editSaveFood,
      editTarget,
      // Delete
      deleteEventHandler,
      deleteDialog,
      deleteFood,
      deleteTarget,
      // Alias Manager
      aliasManagerDialog,
      aliasManagerEventHandler,
      updateFoodAlias,
      // Merge
      canMerge,
      mergeFoods,
      mergeDialog,
      fromFood,
      toFood,
      // Seed Data
      locale,
      locales,
      seedDialog,
      seedDatabase,
    };
  },
});
</script>
