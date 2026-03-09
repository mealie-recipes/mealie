<template>
  <div>
    <!-- Merge Dialog -->
    <BaseDialog
      v-model="mergeDialog"
      :icon="$globals.icons.foods"
      :title="$t('data-pages.foods.combine-food')"
      can-confirm
      @confirm="mergeFoods"
    >
      <v-card-text>
        <div>
          {{ $t("data-pages.foods.merge-dialog-text") }}
        </div>
        <v-autocomplete
          v-model="fromFood"
          return-object
          :items="foods"
          :custom-filter="normalizeFilter"
          item-title="name"
          :label="$t('data-pages.foods.source-food')"
        />
        <v-autocomplete
          v-model="toFood"
          return-object
          :items="foods"
          :custom-filter="normalizeFilter"
          item-title="name"
          :label="$t('data-pages.foods.target-food')"
        />

        <template v-if="canMerge && fromFood && toFood">
          <div class="text-center">
            {{ $t("data-pages.foods.merge-food-example", { food1: fromFood.name, food2: toFood.name }) }}
          </div>
        </template>
      </v-card-text>
    </BaseDialog>

    <!-- Seed Dialog -->
    <BaseDialog
      v-model="seedDialog"
      :icon="$globals.icons.foods"
      :title="$t('data-pages.seed-data')"
      can-confirm
      @confirm="seedDatabase"
    >
      <v-card-text>
        <div class="pb-2">
          {{ $t("data-pages.foods.seed-dialog-text") }}
        </div>
        <v-autocomplete
          v-model="locale"
          :items="locales"
          item-title="name"
          :custom-filter="normalizeFilter"
          :label="$t('data-pages.select-language')"
          class="my-3"
          hide-details
          variant="outlined"
          offset
        >
          <template #item="{ item, props }">
            <v-list-item v-bind="props">
              <v-list-item-subtitle>
                {{ item.raw.progress }}% {{ $t("language-dialog.translated") }}
              </v-list-item-subtitle>
            </v-list-item>
          </template>
        </v-autocomplete>

        <v-alert
          v-if="foods && foods.length > 0"
          type="error"
          class="mb-0 text-body-2"
        >
          {{ $t("data-pages.foods.seed-dialog-warning") }}
        </v-alert>
      </v-card-text>
    </BaseDialog>

    <!-- Alias Sub-Dialog -->
    <RecipeDataAliasManagerDialog
      v-if="editForm.data"
      v-model="aliasManagerDialog"
      :data="editForm.data"
      @submit="updateFoodAlias"
      @cancel="aliasManagerDialog = false"
    />

    <!-- Bulk Assign Labels Dialog -->
    <BaseDialog
      v-model="bulkAssignLabelDialog"
      :title="$t('data-pages.labels.assign-label')"
      :icon="$globals.icons.tags"
      can-confirm
      @confirm="assignSelected"
    >
      <v-card-text>
        <v-card class="mb-4">
          <v-card-title>{{ $t("general.caution") }}</v-card-title>
          <v-card-text>{{ $t("data-pages.foods.label-overwrite-warning") }}</v-card-text>
        </v-card>

        <v-autocomplete
          v-model="bulkAssignLabelId"
          clearable
          :items="allLabels"
          :custom-filter="normalizeFilter"
          item-value="id"
          item-title="name"
          :label="$t('data-pages.foods.food-label')"
        />
        <v-card variant="outlined">
          <v-virtual-scroll
            height="400"
            item-height="25"
            :items="bulkAssignTarget"
          >
            <template #default="{ item }">
              <v-list-item class="pb-2">
                <v-list-item-title>{{ item.name }}</v-list-item-title>
              </v-list-item>
            </template>
          </v-virtual-scroll>
        </v-card>
      </v-card-text>
    </BaseDialog>

    <GroupDataPage
      :icon="$globals.icons.foods"
      :title="$t('data-pages.foods.food-data')"
      :create-title="$t('data-pages.foods.create-food')"
      :edit-title="$t('data-pages.foods.edit-food')"
      :table-headers="tableHeaders"
      :table-config="tableConfig"
      :data="foods || []"
      :bulk-actions="[
        { icon: $globals.icons.delete, text: $t('general.delete'), event: 'delete-selected' },
        { icon: $globals.icons.tags, text: $t('data-pages.labels.assign-label'), event: 'assign-selected' },
      ]"
      :create-form="createForm"
      :edit-form="editForm"
      @create-one="handleCreate"
      @edit-one="handleEdit"
      @delete-one="foodStore.actions.deleteOne"
      @bulk-action="handleBulkAction"
    >
      <template #table-button-row>
        <BaseButton @click="mergeDialog = true">
          <template #icon>
            {{ $globals.icons.externalLink }}
          </template>
          {{ $t('data-pages.combine') }}
        </BaseButton>
      </template>

      <template #[`item.label`]="{ item }">
        <MultiPurposeLabel
          v-if="item.label"
          :label="item.label"
        >
          {{ item.label.name }}
        </MultiPurposeLabel>
      </template>

      <template #[`item.onHand`]="{ item }">
        <v-icon :color="item.onHand ? 'success' : undefined">
          {{ item.onHand ? $globals.icons.check : $globals.icons.close }}
        </v-icon>
      </template>

      <template #[`item.createdAt`]="{ item }">
        {{ item.createdAt ? $d(new Date(item.createdAt)) : '' }}
      </template>

      <template #table-button-bottom>
        <BaseButton @click="seedDialog = true">
          <template #icon>
            {{ $globals.icons.database }}
          </template>
          {{ $t('data-pages.seed') }}
        </BaseButton>
      </template>

      <template #edit-dialog-custom-action>
        <BaseButton
          edit
          @click="aliasManagerDialog = true"
        >
          {{ $t('data-pages.manage-aliases') }}
        </BaseButton>
      </template>
    </GroupDataPage>
  </div>
</template>

<script setup lang="ts">
import type { LocaleObject } from "@nuxtjs/i18n";
import RecipeDataAliasManagerDialog from "~/components/Domain/Recipe/RecipeDataAliasManagerDialog.vue";
import { validators } from "~/composables/use-validators";
import { useUserApi } from "~/composables/api";
import type { CreateIngredientFood, IngredientFood, IngredientFoodAlias } from "~/lib/api/types/recipe";
import MultiPurposeLabel from "~/components/Domain/ShoppingList/MultiPurposeLabel.vue";
import { useLocales } from "~/composables/use-locales";
import { normalizeFilter } from "~/composables/use-utils";
import { useFoodStore, useLabelStore } from "~/composables/store";
import type { MultiPurposeLabelOut } from "~/lib/api/types/labels";
import type { AutoFormItems } from "~/types/auto-forms";
import type { TableHeaders, TableConfig } from "~/components/global/CrudTable.vue";
import { fieldTypes } from "~/composables/forms";

interface CreateIngredientFoodWithOnHand extends CreateIngredientFood {
  onHand: boolean;
  householdsWithIngredientFood: string[];
}

interface IngredientFoodWithOnHand extends IngredientFood {
  onHand: boolean;
}
const userApi = useUserApi();
const i18n = useI18n();
const auth = useMealieAuth();
const tableConfig: TableConfig = {
  hideColumns: true,
  canExport: true,
};
const tableHeaders: TableHeaders[] = [
  {
    text: i18n.t("general.id"),
    value: "id",
    show: false,
  },
  {
    text: i18n.t("general.name"),
    value: "name",
    show: true,
    sortable: true,
  },
  {
    text: i18n.t("general.plural-name"),
    value: "pluralName",
    show: true,
    sortable: true,
  },
  {
    text: i18n.t("recipe.description"),
    value: "description",
    show: true,
  },
  {
    text: i18n.t("shopping-list.label"),
    value: "label",
    show: true,
    sortable: true,
    sort: (label1: MultiPurposeLabelOut | null, label2: MultiPurposeLabelOut | null) => {
      const label1Name = label1?.name || "";
      const label2Name = label2?.name || "";
      return label1Name.localeCompare(label2Name);
    },
  },
  {
    text: i18n.t("tool.on-hand"),
    value: "onHand",
    show: true,
    sortable: true,
  },
  {
    text: i18n.t("general.date-added"),
    value: "createdAt",
    show: false,
    sortable: true,
  },
];

const userHousehold = computed(() => auth.user.value?.householdSlug || "");
const foodStore = useFoodStore();
const foods = computed(() => foodStore.store.value.map((food) => {
  const onHand = food.householdsWithIngredientFood?.includes(userHousehold.value) || false;
  return { ...food, onHand } as IngredientFoodWithOnHand;
}));

// ============================================================
// Labels
const { store: allLabels } = useLabelStore();
const labelOptions = computed(() => allLabels.value.map(label => ({ text: label.name, value: label.id })) || []);

// ============================================================
// Form items (shared)
const formItems = computed<AutoFormItems>(() => [
  {
    label: i18n.t("general.name"),
    varName: "name",
    type: fieldTypes.TEXT,
    rules: [validators.required],
  },
  {
    label: i18n.t("general.plural-name"),
    varName: "pluralName",
    type: fieldTypes.TEXT,
  },
  {
    label: i18n.t("recipe.description"),
    varName: "description",
    type: fieldTypes.TEXT,
  },
  {
    label: i18n.t("data-pages.foods.food-label"),
    varName: "labelId",
    type: fieldTypes.SELECT,
    options: labelOptions.value,
    selectReturnValue: "value",
  },
  {
    label: i18n.t("tool.on-hand"),
    varName: "onHand",
    type: fieldTypes.BOOLEAN,
    hint: i18n.t("data-pages.foods.on-hand-checkbox-label"),
  },
]);

// ===============================================================
// Create

const createForm = reactive({
  get items() {
    return formItems.value;
  },
  data: { name: "", onHand: false, householdsWithIngredientFood: [] } as CreateIngredientFoodWithOnHand,
});

async function handleCreate() {
  if (!createForm.data || !createForm.data.name) {
    return;
  }

  if (createForm.data.onHand) {
    createForm.data.householdsWithIngredientFood = [userHousehold.value];
  }

  // @ts-expect-error the createOne function erroneously expects an id because it uses the IngredientFood type
  await foodStore.actions.createOne(createForm.data);
  createForm.data = {
    name: "",
    onHand: false,
    householdsWithIngredientFood: [],
  };
}

// ===============================================================
// Edit

const editForm = reactive({
  get items() {
    return formItems.value;
  },
  data: {} as IngredientFoodWithOnHand,
});

async function handleEdit() {
  if (!editForm.data) {
    return;
  }
  if (!editForm.data.householdsWithIngredientFood) {
    editForm.data.householdsWithIngredientFood = [];
  }

  if (editForm.data.onHand && !editForm.data.householdsWithIngredientFood.includes(userHousehold.value)) {
    editForm.data.householdsWithIngredientFood.push(userHousehold.value);
  }
  else if (!editForm.data.onHand && editForm.data.householdsWithIngredientFood.includes(userHousehold.value)) {
    const idx = editForm.data.householdsWithIngredientFood.indexOf(userHousehold.value);
    if (idx !== -1) editForm.data.householdsWithIngredientFood.splice(idx, 1);
  }

  await foodStore.actions.updateOne(editForm.data);
  editForm.data = {} as IngredientFoodWithOnHand;
}

// ============================================================
// Bulk Actions
async function handleBulkAction(event: string, items: IngredientFoodWithOnHand[]) {
  if (event === "delete-selected") {
    const ids = items.map(item => item.id);
    await foodStore.actions.deleteMany(ids);
  }
  else if (event === "assign-selected") {
    bulkAssignEventHandler(items);
  }
}

// ============================================================
// Alias Manager

const aliasManagerDialog = ref(false);
function updateFoodAlias(newAliases: IngredientFoodAlias[]) {
  if (!editForm.data) {
    return;
  }
  editForm.data.aliases = newAliases;
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
// Seed

const seedDialog = ref(false);
const locale = ref("");

const { locales: LOCALES, locale: currentLocale } = useLocales();

onMounted(() => {
  locale.value = currentLocale.value;
});

const locales = LOCALES.filter(locale =>
  (i18n.locales.value as LocaleObject[]).map(i18nLocale => i18nLocale.code).includes(locale.value as any),
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
</script>
