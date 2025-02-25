<template>
  <div>
    <!-- Merge Dialog -->
    <BaseDialog v-model="mergeDialog" :icon="$globals.icons.foods" :title="$tc('data-pages.foods.combine-food')" @confirm="mergeFoods">
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
      :title="$tc('data-pages.foods.create-food')"
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
          <v-checkbox
            v-model="createTarget.onHand"
            hide-details
            :label="$t('tool.on-hand')"
          />
          <p class="text-caption mt-1">
            {{ $t("data-pages.foods.on-hand-checkbox-label") }}
          </p>
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
      :title="$tc('data-pages.foods.edit-food')"
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
          <v-checkbox
            v-model="editTarget.onHand"
            hide-details
            :label="$t('tool.on-hand')"
          />
          <p class="text-caption mt-1">
            {{ $t("data-pages.foods.on-hand-checkbox-label") }}
          </p>
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
        {{ $t("general.confirm-delete-generic") }}
        <p v-if="deleteTarget" class="mt-4 ml-4">{{ deleteTarget.name }}</p>
      </v-card-text>
    </BaseDialog>

    <!-- Bulk Delete Dialog -->
    <BaseDialog
      v-model="bulkDeleteDialog"
      width="650px"
      :title="$tc('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      @confirm="deleteSelected"
    >
      <v-card-text>
        <p class="h4">{{ $t('general.confirm-delete-generic-items') }}</p>
        <v-card outlined>
          <v-virtual-scroll height="400" item-height="25" :items="bulkDeleteTarget">
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

    <!-- Bulk Assign Labels Dialog -->
    <BaseDialog
      v-model="bulkAssignLabelDialog"
      :title="$tc('data-pages.labels.assign-label')"
      :icon="$globals.icons.tags"
      @confirm="assignSelected"
    >
      <v-card-text>
        <v-card class="mb-4">
          <v-card-title>{{ $tc("general.caution") }}</v-card-title>
          <v-card-text>{{ $tc("data-pages.foods.label-overwrite-warning") }}</v-card-text>
        </v-card>

        <v-autocomplete
          v-model="bulkAssignLabelId"
          clearable
          :items="allLabels"
          item-value="id"
          item-text="name"
          :label="$tc('data-pages.foods.food-label')"
        />
        <v-card outlined>
          <v-virtual-scroll height="400" item-height="25" :items="bulkAssignTarget">
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

    <!-- Data Table -->
    <BaseCardSectionTitle :icon="$globals.icons.foods" section :title="$tc('data-pages.foods.food-data')"> </BaseCardSectionTitle>
    <CrudTable
      :table-config="tableConfig"
      :headers.sync="tableHeaders"
      :data="foods || []"
      :bulk-actions="[
        {icon: $globals.icons.delete, text: $tc('general.delete'), event: 'delete-selected'},
        {icon: $globals.icons.tags, text: $tc('data-pages.labels.assign-label'), event: 'assign-selected'}
      ]"
      initial-sort="createdAt"
      initial-sort-desc
      @delete-one="deleteEventHandler"
      @edit-one="editEventHandler"
      @create-one="createEventHandler"
      @delete-selected="bulkDeleteEventHandler"
      @assign-selected="bulkAssignEventHandler"
    >
      <template #button-row>
        <BaseButton create @click="createDialog = true" />
        <BaseButton @click="mergeDialog = true">
          <template #icon> {{ $globals.icons.externalLink }} </template>
          {{ $t('data-pages.combine') }}
        </BaseButton>
      </template>
      <template #item.label="{ item }">
        <MultiPurposeLabel v-if="item.label" :label="item.label">
          {{ item.label.name }}
        </MultiPurposeLabel>
      </template>
      <template #item.onHand="{ item }">
        <v-icon :color="item.onHand ? 'success' : undefined">
          {{ item.onHand ? $globals.icons.check : $globals.icons.close }}
        </v-icon>
      </template>
      <template #item.createdAt="{ item }">
        {{ formatDate(item.createdAt) }}
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
import { MultiPurposeLabelOut } from "~/lib/api/types/labels";

interface CreateIngredientFoodWithOnHand extends CreateIngredientFood {
  onHand: boolean;
  householdsWithIngredientFood: string[];
}

interface IngredientFoodWithOnHand extends IngredientFood {
  onHand: boolean;
}

export default defineComponent({
  components: { MultiPurposeLabel, RecipeDataAliasManagerDialog },
  setup() {
    const userApi = useUserApi();
    const { $auth, i18n } = useContext();
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
        sort: (label1: MultiPurposeLabelOut | null, label2: MultiPurposeLabelOut | null) => {
          const label1Name = label1?.name || "";
          const label2Name = label2?.name || "";
          return label1Name.localeCompare(label2Name);
        },
      },
      {
        text: i18n.tc("tool.on-hand"),
        value: "onHand",
        show: true,
      },
      {
        text: i18n.tc("general.date-added"),
        value: "createdAt",
        show: false,
      }
    ];

    function formatDate(date: string) {
      try {
        return i18n.d(Date.parse(date), "medium");
      } catch {
        return "";
      }
    }

    const userHousehold = computed(() => $auth.user?.householdSlug || "");
    const foodStore = useFoodStore();
    const foods = computed(() => foodStore.store.value.map((food) => {
      const onHand = food.householdsWithIngredientFood?.includes(userHousehold.value) || false;
      return { ...food, onHand } as IngredientFoodWithOnHand;
    }));

    // ===============================================================
    // Food Creator

    const domNewFoodForm = ref<VForm>();
    const createDialog = ref(false);
    const createTarget = ref<CreateIngredientFoodWithOnHand>({
      name: "",
      onHand: false,
      householdsWithIngredientFood: [],
    });

    function createEventHandler() {
      createDialog.value = true;
    }

    async function createFood() {
      if (!createTarget.value || !createTarget.value.name) {
        return;
      }

      if (createTarget.value.onHand) {
        createTarget.value.householdsWithIngredientFood = [userHousehold.value];
      }

      // @ts-expect-error the createOne function erroneously expects an id because it uses the IngredientFood type
      await foodStore.actions.createOne(createTarget.value);
      createDialog.value = false;

      domNewFoodForm.value?.reset();
      createTarget.value = {
        name: "",
        onHand: false,
        householdsWithIngredientFood: [],
      };
    }

    // ===============================================================
    // Food Editor

    const editDialog = ref(false);
    const editTarget = ref<IngredientFoodWithOnHand | null>(null);

    function editEventHandler(item: IngredientFoodWithOnHand) {
      editTarget.value = item;
      editTarget.value.onHand = item.householdsWithIngredientFood?.includes(userHousehold.value) || false;
      editDialog.value = true;
    }

    async function editSaveFood() {
      if (!editTarget.value) {
        return;
      }
      if (editTarget.value.onHand && !editTarget.value.householdsWithIngredientFood?.includes(userHousehold.value)) {
        if (!editTarget.value.householdsWithIngredientFood) {
          editTarget.value.householdsWithIngredientFood = [userHousehold.value];
        } else {
          editTarget.value.householdsWithIngredientFood.push(userHousehold.value);
        }
      } else if (!editTarget.value.onHand && editTarget.value.householdsWithIngredientFood?.includes(userHousehold.value)) {
        editTarget.value.householdsWithIngredientFood = editTarget.value.householdsWithIngredientFood.filter(
          (household) => household !== userHousehold.value
        );
      }

      await foodStore.actions.updateOne(editTarget.value);
      editDialog.value = false;
    }

    // ===============================================================
    // Food Delete

    const deleteDialog = ref(false);
    const deleteTarget = ref<IngredientFoodWithOnHand | null>(null);
    function deleteEventHandler(item: IngredientFoodWithOnHand) {
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

    const bulkDeleteDialog = ref(false);
    const bulkDeleteTarget = ref<IngredientFoodWithOnHand[]>([]);

    function bulkDeleteEventHandler(selection: IngredientFoodWithOnHand[]) {
      bulkDeleteTarget.value = selection;
      bulkDeleteDialog.value = true;
    }

    async function deleteSelected() {
      for (const item of bulkDeleteTarget.value) {
        await foodStore.actions.deleteOne(item.id);
      }
      bulkDeleteTarget.value = [];
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
    const fromFood = ref<IngredientFoodWithOnHand | null>(null);
    const toFood = ref<IngredientFoodWithOnHand | null>(null);

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

    const { store: allLabels } = useLabelStore();

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

    // ============================================================
    // Bulk Assign Labels
    const bulkAssignLabelDialog = ref(false);
    const bulkAssignTarget = ref<IngredientFoodWithOnHand[]>([]);
    const bulkAssignLabelId = ref<string | undefined>();

    function bulkAssignEventHandler(selection: IngredientFoodWithOnHand[]) {
      bulkAssignTarget.value = selection;
      bulkAssignLabelDialog.value = true;
    }

    async function assignSelected() {
      if (!bulkAssignLabelId.value) {
        return;
      }
      for (const item of bulkAssignTarget.value) {
        item.labelId = bulkAssignLabelId.value;
        await foodStore.actions.updateOne(item);
      }
      bulkAssignTarget.value = [];
      bulkAssignLabelId.value = undefined;
      foodStore.actions.refresh();
    }

    return {
      tableConfig,
      tableHeaders,
      foods,
      allLabels,
      validators,
      formatDate,
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
      bulkDeleteDialog,
      bulkDeleteTarget,
      bulkDeleteEventHandler,
      deleteSelected,
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
      // Bulk Assign Labels
      bulkAssignLabelDialog,
      bulkAssignTarget,
      bulkAssignLabelId,
      bulkAssignEventHandler,
      assignSelected,
    };
  },
});
</script>
