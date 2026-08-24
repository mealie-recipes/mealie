<template>
  <div>
    <!-- Merge Dialog -->
    <BaseDialog
      v-model="mergeDialog"
      :icon="$globals.icons.units"
      :title="$t('data-pages.units.combine-unit')"
      can-confirm
      @confirm="mergeUnits"
    >
      <v-card-text>
        <i18n-t keypath="data-pages.units.combine-unit-description">
          <template #source-unit-will-be-deleted>
            <strong> {{ $t('data-pages.recipes.source-unit-will-be-deleted') }} </strong>
          </template>
        </i18n-t>

        <v-autocomplete
          v-model="fromUnit"
          return-object
          :items="unitStore"
          :custom-filter="normalizeFilter"
          item-title="name"
          :label="$t('data-pages.units.source-unit')"
          class="mt-2"
        />
        <v-autocomplete
          v-model="toUnit"
          return-object
          :items="unitStore"
          :custom-filter="normalizeFilter"
          item-title="name"
          :label="$t('data-pages.units.target-unit')"
        />

        <template v-if="canMerge && fromUnit && toUnit">
          <div class="text-center">
            {{ $t('data-pages.units.merging-unit-into-unit', [fromUnit.name, toUnit.name]) }}
          </div>
        </template>
      </v-card-text>
    </BaseDialog>

    <!-- Alias Sub-Dialog -->
    <RecipeDataAliasManagerDialog
      v-if="editForm.data"
      v-model="aliasManagerDialog"
      :data="editForm.data"
      can-submit
      @submit="updateUnitAlias"
      @cancel="aliasManagerDialog = false"
    />

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
          {{ $t("data-pages.units.seed-dialog-text") }}
        </div>
        <v-autocomplete
          v-model="locale"
          :items="locales"
          item-title="name"
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
          v-if="unitStore && unitStore.length > 0"
          type="error"
          class="mb-0 text-body-2"
        >
          {{ $t("data-pages.foods.seed-dialog-warning") }}
        </v-alert>
      </v-card-text>
    </BaseDialog>

    <GroupDataPage
      :icon="$globals.icons.units"
      :title="$t('general.units')"
      :create-title="$t('data-pages.units.create-unit')"
      :edit-title="$t('data-pages.units.edit-unit')"
      :table-headers="tableHeaders"
      :table-config="tableConfig"
      :data="unitStore || []"
      :bulk-actions="[{ icon: $globals.icons.delete, text: $t('general.delete'), event: 'delete-selected' }]"
      :create-form="createForm"
      :edit-form="editForm"
      @create-one="handleCreate"
      @edit-one="handleEdit"
      @delete-one="unitActions.deleteOne"
      @bulk-action="handleBulkAction"
    >
      <template #table-button-row>
        <BaseButton
          :icon="$globals.icons.externalLink"
          @click="mergeDialog = true"
        >
          {{ $t('data-pages.combine') }}
        </BaseButton>
      </template>

      <template #[`item.useAbbreviation`]="{ item }">
        <v-icon :color="item.useAbbreviation ? 'success' : undefined">
          {{ item.useAbbreviation ? $globals.icons.check : $globals.icons.close }}
        </v-icon>
      </template>

      <template #[`item.fraction`]="{ item }">
        <v-icon :color="item.fraction ? 'success' : undefined">
          {{ item.fraction ? $globals.icons.check : $globals.icons.close }}
        </v-icon>
      </template>

      <template #[`item.createdAt`]="{ item }">
        {{ item.createdAt ? $d(new Date(item.createdAt)) : '' }}
      </template>

      <template #table-button-bottom>
        <BaseButton :icon="$globals.icons.database" @click="seedDialog = true">
          {{ $t('data-pages.seed') }}
        </BaseButton>
      </template>

      <template #edit-dialog-custom-action>
        <BaseButton
          :icon="$globals.icons.tags"
          color="info"
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
import type { CreateIngredientUnit, IngredientUnit, IngredientUnitAlias } from "~/lib/api/types/recipe";
import type { StandardizedUnitType } from "~/lib/api/types/non-generated";
import { useLocales } from "~/composables/use-locales";
import { normalizeFilter } from "~/composables/use-utils";
import { useUnitStore } from "~/composables/store";
import type { AutoFormItems } from "~/types/auto-forms";
import type { TableHeaders, TableConfig } from "~/components/global/CrudTable.vue";
import { fieldTypes } from "~/composables/forms";

const userApi = useUserApi();
const i18n = useI18n();

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
    text: i18n.t("data-pages.units.abbreviation"),
    value: "abbreviation",
    show: true,
    sortable: true,
  },
  {
    text: i18n.t("data-pages.units.plural-abbreviation"),
    value: "pluralAbbreviation",
    show: true,
    sortable: true,
  },
  {
    text: i18n.t("data-pages.units.use-abbv"),
    value: "useAbbreviation",
    show: true,
    sortable: true,
  },
  {
    text: i18n.t("data-pages.units.description"),
    value: "description",
    show: false,
  },
  {
    text: i18n.t("data-pages.units.fraction"),
    value: "fraction",
    show: true,
    sortable: true,
  },
  {
    text: i18n.t("data-pages.units.standard-quantity"),
    value: "standardQuantity",
    show: false,
  },
  {
    text: i18n.t("data-pages.units.standard-unit"),
    value: "standardUnit",
    show: false,
  },
  {
    text: i18n.t("general.date-added"),
    value: "createdAt",
    show: false,
    sortable: true,
  },
];

const { store: unitStore, actions: unitActions } = useUnitStore();

// ============================================================
// Form items (shared)
type StandardizedUnitTypeOption = {
  text: string;
  value: StandardizedUnitType;
};

const formItems = computed<AutoFormItems>(() => [
  {
    cols: 8,
    label: i18n.t("general.name"),
    varName: "name",
    type: fieldTypes.TEXT,
    rules: [validators.required],
  },
  {
    cols: 4,
    label: i18n.t("data-pages.units.abbreviation"),
    varName: "abbreviation",
    type: fieldTypes.TEXT,
  },
  {
    cols: 8,
    label: i18n.t("general.plural-name"),
    varName: "pluralName",
    type: fieldTypes.TEXT,
  },
  {
    cols: 4,
    label: i18n.t("data-pages.units.plural-abbreviation"),
    varName: "pluralAbbreviation",
    type: fieldTypes.TEXT,
  },
  {
    label: i18n.t("data-pages.units.description"),
    varName: "description",
    type: fieldTypes.TEXT,
  },
  {
    section: i18n.t("data-pages.units.standardization"),
    sectionDetails: i18n.t("data-pages.units.standardization-description"),
    cols: 2,
    varName: "standardQuantity",
    type: fieldTypes.NUMBER,
    numberInputConfig: {
      min: 0,
      max: undefined,
      precision: null,
      controlVariant: "hidden",
    },
  },
  {
    cols: 10,
    varName: "standardUnit",
    type: fieldTypes.SELECT,
    selectReturnValue: "value",
    options: [
      {
        text: i18n.t("data-pages.units.standard-unit-labels.fluid-ounce"),
        value: "fluid_ounce",
      },
      {
        text: i18n.t("data-pages.units.standard-unit-labels.cup"),
        value: "cup",
      },
      {
        text: i18n.t("data-pages.units.standard-unit-labels.ounce"),
        value: "ounce",
      },
      {
        text: i18n.t("data-pages.units.standard-unit-labels.pound"),
        value: "pound",
      },
      {
        text: i18n.t("data-pages.units.standard-unit-labels.milliliter"),
        value: "milliliter",
      },
      {
        text: i18n.t("data-pages.units.standard-unit-labels.liter"),
        value: "liter",
      },
      {
        text: i18n.t("data-pages.units.standard-unit-labels.gram"),
        value: "gram",
      },
      {
        text: i18n.t("data-pages.units.standard-unit-labels.kilogram"),
        value: "kilogram",
      },
    ] as StandardizedUnitTypeOption[],
  },
  {
    section: i18n.t("general.settings"),
    cols: 4,
    label: i18n.t("data-pages.units.use-abbv"),
    varName: "useAbbreviation",
    type: fieldTypes.BOOLEAN,
  },
  {
    cols: 4,
    label: i18n.t("data-pages.units.fraction"),
    varName: "fraction",
    type: fieldTypes.BOOLEAN,
  },
]);

// ============================================================
// Create
const createForm = reactive({
  items: formItems,
  data: {
    name: "",
    fraction: false,
    useAbbreviation: false,
  } as CreateIngredientUnit,
});

async function handleCreate(createFormData: CreateIngredientUnit) {
  // @ts-expect-error createOne eroniusly expects id which is not preset at time of creation
  await unitActions.createOne(createFormData);
  createForm.data = {
    name: "",
    fraction: false,
    useAbbreviation: false,
  } as CreateIngredientUnit;
}

// ============================================================
// Edit
const editForm = reactive({
  items: formItems,
  data: {} as IngredientUnit,
});

async function handleEdit(editFormData: IngredientUnit) {
  await unitActions.updateOne(editFormData);
  editForm.data = {} as IngredientUnit;
}

// ============================================================
// Bulk Actions
async function handleBulkAction(event: string, items: IngredientUnit[]) {
  if (event === "delete-selected") {
    const ids = items.filter(item => item.id != null).map(item => item.id!);
    await unitActions.deleteMany(ids);
  }
}

// ============================================================
// Alias Manager

const aliasManagerDialog = ref(false);
function updateUnitAlias(newAliases: IngredientUnitAlias[]) {
  if (!editForm.data) {
    return;
  }
  editForm.data.aliases = newAliases;
  aliasManagerDialog.value = false;
}

// ============================================================
// Merge Units

const mergeDialog = ref(false);
const fromUnit = ref<IngredientUnit | null>(null);
const toUnit = ref<IngredientUnit | null>(null);

const canMerge = computed(() => {
  return fromUnit.value && toUnit.value && fromUnit.value.id !== toUnit.value.id;
});

async function mergeUnits() {
  if (!canMerge.value || !fromUnit.value || !toUnit.value) {
    return;
  }

  const { data } = await userApi.units.merge(fromUnit.value.id, toUnit.value.id);

  if (data) {
    unitActions.refresh();
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
  const { data } = await userApi.seeders.units({ locale: locale.value });

  if (data) {
    unitActions.refresh();
  }
}
</script>
