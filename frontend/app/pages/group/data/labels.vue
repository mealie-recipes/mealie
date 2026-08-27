<template>
  <div>
    <!-- Merge Dialog -->
    <BaseDialog
      v-model="mergeDialog"
      :icon="$globals.icons.tags"
      :title="$t('data-pages.labels.combine-label')"
      can-confirm
      @confirm="mergeLabels"
      @close="resetMergeDialog"
    >
      <v-card-text>
        <div>
          {{ $t("data-pages.labels.merge-dialog-text") }}
        </div>
        <v-autocomplete
          v-model="fromLabel"
          return-object
          :items="labelStore.store.value"
          :custom-filter="normalizeFilter"
          item-title="name"
          :label="$t('data-pages.labels.source-label')"
        />
        <v-autocomplete
          v-model="toLabel"
          return-object
          :items="labelStore.store.value"
          :custom-filter="normalizeFilter"
          item-title="name"
          :label="$t('data-pages.labels.target-label')"
        />

        <template v-if="canMerge && fromLabel && toLabel">
          <div class="text-center">
            {{ $t("data-pages.labels.merge-label-example", { label1: fromLabel.name, label2: toLabel.name }) }}
          </div>
        </template>
      </v-card-text>
    </BaseDialog>

    <!-- Delete Unused Dialog -->
    <BaseDialog
      v-model="deleteUnusedDialog"
      :title="$t('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      can-confirm
      @confirm="confirmDeleteUnused"
    >
      <v-card-text>
        {{ $t('data-pages.labels.delete-unused-confirm', { count: unusedLabelIds.length }, unusedLabelIds.length) }}
        <ul style="margin: 0.5rem 0 0; padding-left: 1.25rem; font-size: 0.85rem; color: rgba(var(--v-theme-on-surface), 0.7); line-height: 1.8;">
          <li v-for="name in unusedLabelNamesPreview" :key="name">
            {{ name }}
          </li>
        </ul>
        <div v-if="unusedLabelNamesRemaining > 0" class="text-body-2 pl-2">
          {{ $t('data-pages.delete-unused-more', { count: unusedLabelNamesRemaining }) }}
        </div>
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
          {{ $t("data-pages.labels.seed-dialog-text") }}
        </div>
        <v-autocomplete
          v-model="locale"
          :items="locales"
          :custom-filter="normalizeFilter"
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
          v-if="labelStore.store.value && labelStore.store.value.length > 0"
          type="error"
          class="mb-0 text-body-2"
        >
          {{ $t("data-pages.foods.seed-dialog-warning") }}
        </v-alert>
      </v-card-text>
    </BaseDialog>

    <GroupDataPage
      :icon="$globals.icons.tags"
      :title="$t('data-pages.labels.labels')"
      :create-title="$t('data-pages.labels.new-label')"
      :edit-title="$t('data-pages.labels.edit-label')"
      :table-headers="tableHeaders"
      :table-config="tableConfig"
      :data="labelStore.store.value || []"
      :bulk-actions="[{ icon: $globals.icons.delete, text: $t('general.delete'), event: 'delete-selected' }]"
      :create-form="createForm"
      :edit-form="editForm"
      @create-one="handleCreate"
      @edit-one="handleEdit"
      @delete-one="labelStore.actions.deleteOne"
      @bulk-action="handleBulkAction"
    >
      <template #[`item.name`]="{ item }">
        <MultiPurposeLabel
          v-if="item"
          :label="item"
        >
          {{ item.name }}
        </MultiPurposeLabel>
      </template>

      <template #create-dialog-top>
        <MultiPurposeLabel v-if="createForm.data.name" :label="createForm.data" class="my-2" />
      </template>

      <template #edit-dialog-top>
        <MultiPurposeLabel v-if="editForm.data.name" :label="editForm.data" class="my-2" />
      </template>

      <template #table-button-row>
        <BaseButton @click="mergeDialog = true">
          <template #icon>
            {{ $globals.icons.externalLink }}
          </template>
          {{ $t("data-pages.combine") }}
        </BaseButton>

        <v-divider vertical class="mx-2" />

        <BaseButton color="error" :loading="loadingEmpty" @click="openDeleteUnusedDialog">
          <template #icon>
            {{ $globals.icons.broom }}
          </template>
          {{ $t("data-pages.delete-unused") }}
        </BaseButton>
      </template>

      <template #table-button-bottom>
        <BaseButton @click="seedDialog = true">
          <template #icon>
            {{ $globals.icons.database }}
          </template>
          {{ $t('data-pages.seed') }}
        </BaseButton>
      </template>
    </GroupDataPage>
  </div>
</template>

<script setup lang="ts">
import { validators } from "~/composables/use-validators";
import { useUserApi } from "~/composables/api";
import MultiPurposeLabel from "~/components/Domain/ShoppingList/MultiPurposeLabel.vue";
import { fieldTypes } from "~/composables/forms";
import type { MultiPurposeLabelOut, MultiPurposeLabelSummary } from "~/lib/api/types/labels";
import type { AutoFormItems } from "~/types/auto-forms";
import { useLocales } from "~/composables/use-locales";
import { normalizeFilter } from "~/composables/use-utils";
import { alert } from "~/composables/use-toast";
import { useLabelStore } from "~/composables/store";
import type { TableHeaders, TableConfig } from "~/components/global/CrudTable.vue";

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
];

const labelStore = useLabelStore();

// ============================================================
// Form items (shared)
const formItems: AutoFormItems = [
  {
    label: i18n.t("general.name"),
    varName: "name",
    type: fieldTypes.TEXT,
    rules: [validators.required],
  },
  {
    label: i18n.t("general.color"),
    varName: "color",
    type: fieldTypes.COLOR,
  },
];

// ============================================================
// Create
const createForm = reactive({
  items: formItems,
  data: {
    name: "",
    color: "",
  } as MultiPurposeLabelSummary,
});

async function handleCreate(createFormData: MultiPurposeLabelSummary) {
  await labelStore.actions.createOne(createFormData);
  createForm.data = { name: "", color: "#7417BE" } as MultiPurposeLabelSummary;
}

// ============================================================
// Edit
const editForm = reactive({
  items: formItems,
  data: {} as MultiPurposeLabelSummary,
});

async function handleEdit(editFormData: MultiPurposeLabelSummary) {
  await labelStore.actions.updateOne(editFormData);
  editForm.data = {} as MultiPurposeLabelSummary;
}

// ============================================================
// Bulk Actions
async function handleBulkAction(event: string, items: MultiPurposeLabelSummary[]) {
  if (event === "delete-selected") {
    const ids = items.filter(item => item.id != null).map(item => item.id!);
    await labelStore.actions.deleteMany(ids);
  }
}

// ============================================================
// Merge Labels
const mergeDialog = ref(false);
const fromLabel = ref<MultiPurposeLabelOut | null>(null);
const toLabel = ref<MultiPurposeLabelOut | null>(null);

const canMerge = computed(() => {
  return fromLabel.value && toLabel.value && fromLabel.value.id !== toLabel.value.id;
});

function resetMergeDialog() {
  fromLabel.value = null;
  toLabel.value = null;
}

async function mergeLabels() {
  if (!canMerge.value || !fromLabel.value?.id || !toLabel.value?.id) {
    return;
  }

  const { data } = await userApi.multiPurposeLabels.merge(fromLabel.value.id, toLabel.value.id);

  if (data) {
    fromLabel.value = null;
    toLabel.value = null;
    labelStore.actions.refresh();
  }
}

// ============================================================
// Delete Unused
const DELETE_UNUSED_PREVIEW_LIMIT = 10;

const deleteUnusedDialog = ref(false);
const unusedLabels = ref<MultiPurposeLabelOut[]>([]);
const unusedLabelIds = computed(() => unusedLabels.value.filter(l => l.id != null).map(l => l.id!));
const unusedLabelNamesPreview = computed(() => unusedLabels.value.slice(0, DELETE_UNUSED_PREVIEW_LIMIT).map(l => l.name));
const unusedLabelNamesRemaining = computed(() => Math.max(unusedLabels.value.length - DELETE_UNUSED_PREVIEW_LIMIT, 0));
const loadingEmpty = ref(false);

async function openDeleteUnusedDialog() {
  loadingEmpty.value = true;
  const { data } = await userApi.multiPurposeLabels.getEmpty();
  loadingEmpty.value = false;
  unusedLabels.value = data ?? [];

  if (unusedLabels.value.length === 0) {
    alert.info(i18n.t("data-pages.labels.no-unused-labels"));
    return;
  }

  deleteUnusedDialog.value = true;
}

async function confirmDeleteUnused() {
  await labelStore.actions.deleteMany(unusedLabelIds.value);
  unusedLabels.value = [];
}

// ============================================================
// Seed

const seedDialog = ref(false);
const locale = ref("");

const { locales: locales, locale: currentLocale } = useLocales();

onMounted(() => {
  locale.value = currentLocale.value;
});

async function seedDatabase() {
  const { data } = await userApi.seeders.labels({ locale: locale.value });

  if (data) {
    labelStore.actions.refresh();
  }
}
</script>
