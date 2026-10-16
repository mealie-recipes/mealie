<template>
  <div>
    <!-- Merge Dialog -->
    <BaseDialog
      v-model="mergeDialog"
      :icon="$globals.icons.tools"
      :title="$t('data-pages.tools.combine-tool')"
      can-confirm
      @confirm="mergeTools"
      @close="resetMergeDialog"
    >
      <v-card-text>
        <div>
          {{ $t("data-pages.tools.merge-dialog-text") }}
        </div>
        <v-autocomplete
          v-model="fromTool"
          return-object
          :items="tools"
          :custom-filter="normalizeFilter"
          item-title="name"
          :label="$t('data-pages.tools.source-tool')"
        />
        <v-autocomplete
          v-model="toTool"
          return-object
          :items="tools"
          :custom-filter="normalizeFilter"
          item-title="name"
          :label="$t('data-pages.tools.target-tool')"
        />

        <template v-if="canMerge && fromTool && toTool">
          <div class="text-center">
            {{ $t("data-pages.tools.merge-tool-example", { tool1: fromTool.name, tool2: toTool.name }) }}
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
        {{ $t('data-pages.tools.delete-unused-confirm', { count: unusedToolIds.length }, unusedToolIds.length) }}
        <ul style="margin: 0.5rem 0 0; padding-left: 1.25rem; font-size: 0.85rem; color: rgba(var(--v-theme-on-surface), 0.7); line-height: 1.8;">
          <li v-for="name in unusedToolNamesPreview" :key="name">
            {{ name }}
          </li>
        </ul>
        <div v-if="unusedToolNamesRemaining > 0" class="text-body-2 pl-2">
          {{ $t('data-pages.delete-unused-more', { count: unusedToolNamesRemaining }) }}
        </div>
      </v-card-text>
    </BaseDialog>

    <!-- Seed Dialog -->
    <BaseDialog
      v-model="seedDialog"
      bottom-sheet
      :icon="$globals.icons.tools"
      :title="$t('data-pages.seed-data')"
      can-confirm
      @confirm="seedDatabase"
    >
      <v-card-text>
        <div class="pb-2">
          {{ $t("data-pages.tools.seed-dialog-text") }}
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
        >
          <template #item="{ item, props }">
            <v-list-item v-bind="props">
              <v-list-item-subtitle>
                {{ item.raw.progress }}% {{ $t("language-dialog.translated") }}
              </v-list-item-subtitle>
            </v-list-item>
          </template>
        </v-autocomplete>

        <v-alert v-if="tools && tools.length > 0" type="error" class="mb-0 text-body-2">
          {{ $t("data-pages.tools.seed-dialog-warning") }}
        </v-alert>
      </v-card-text>
    </BaseDialog>

    <GroupDataPage
      :icon="$globals.icons.tools"
      :title="$t('data-pages.tools.tool-data')"
      :create-title="$t('data-pages.tools.new-tool')"
      :edit-title="$t('data-pages.tools.edit-tool')"
      :table-headers="tableHeaders"
      :table-config="tableConfig"
      :data="tools || []"
      :bulk-actions="[{ icon: $globals.icons.delete, text: $t('general.delete'), event: 'delete-selected' }]"
      :create-form="createForm"
      :edit-form="editForm"
      @create-one="handleCreate"
      @edit-one="handleEdit"
      @delete-one="toolStore.actions.deleteOne"
      @bulk-action="handleBulkAction"
    >
      <template #[`item.recipeCount`]="{ item }">
        <NuxtLink v-if="groupSlug && item.recipeCount > 0" :to="`/g/${groupSlug}?tools=${item.id}`">{{ item.recipeCount }}</NuxtLink>
        <span v-else>{{ item.recipeCount || 0 }}</span>
      </template>

      <template #[`item.onHand`]="{ item }">
        <v-icon :color="item.onHand ? 'success' : undefined">
          {{ item.onHand ? $globals.icons.check : $globals.icons.close }}
        </v-icon>
      </template>

      <template #[`item.family`]="{ item }">
        {{ item.family ? $t(`data-pages.tools.family-${item.family.replace(/_/g, '-')}`) : "" }}
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
          {{ $t("data-pages.seed") }}
        </BaseButton>
      </template>
    </GroupDataPage>
  </div>
</template>

<script setup lang="ts">
import type { LocaleObject } from "@nuxtjs/i18n";
import { validators } from "~/composables/use-validators";
import { fieldTypes } from "~/composables/forms";
import { normalizeFilter } from "~/composables/use-utils";
import { alert } from "~/composables/use-toast";
import { useLocales } from "~/composables/use-locales";
import type { AutoFormItems } from "~/types/auto-forms";
import { useToolStore } from "~/composables/store";
import { useUserApi } from "~/composables/api";
import type { RecipeTool, RecipeToolCreate } from "~/lib/api/types/recipe";
import type { TableHeaders, TableConfig } from "~/components/global/CrudTable.vue";

interface RecipeToolWithOnHand extends RecipeTool {
  onHand: boolean;
}

const i18n = useI18n();
const auth = useMealieAuth();
const groupSlug = computed(() => auth.user.value?.groupSlug || "");
const userApi = useUserApi();

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
    text: i18n.t("data-pages.recipe-count"),
    value: "recipeCount",
    show: true,
    sortable: true,
  },
  {
    text: i18n.t("tool.on-hand"),
    value: "onHand",
    show: true,
    sortable: true,
  },
  {
    text: i18n.t("data-pages.tools.family"),
    value: "family",
    show: true,
    sortable: true,
  },
  {
    text: i18n.t("data-pages.tools.category"),
    value: "category",
    show: true,
    sortable: true,
  },
  {
    text: i18n.t("data-pages.tools.brand"),
    value: "brand",
    show: true,
    sortable: true,
  },
  {
    text: i18n.t("data-pages.tools.model"),
    value: "model",
    show: true,
    sortable: true,
  },
];

const familyOptions = [
  { text: i18n.t("data-pages.tools.family-small-appliance"), value: "small_appliance" },
  { text: i18n.t("data-pages.tools.family-large-appliance"), value: "large_appliance" },
  { text: i18n.t("data-pages.tools.family-manual-tool"), value: "manual_tool" },
  { text: i18n.t("data-pages.tools.family-cookware"), value: "cookware" },
  { text: i18n.t("data-pages.tools.family-bakeware"), value: "bakeware" },
  { text: i18n.t("data-pages.tools.family-other"), value: "other" },
];

const userHousehold = computed(() => auth.user.value?.householdSlug || "");
const toolStore = useToolStore();
const tools = computed(() => toolStore.store.value.map((tool) => {
  const onHand = tool.householdsWithTool?.includes(userHousehold.value) || false;
  return { ...tool, onHand } as RecipeToolWithOnHand;
}));

onMounted(() => {
  toolStore.actions.refresh();
});

// ============================================================
// Form items (shared)
const formItems = [
  {
    label: i18n.t("general.name"),
    varName: "name",
    type: fieldTypes.TEXT,
    rules: [validators.required],
  },
  {
    label: i18n.t("tool.on-hand"),
    varName: "onHand",
    type: fieldTypes.BOOLEAN,
  },
  {
    label: i18n.t("data-pages.tools.family"),
    varName: "family",
    type: fieldTypes.SELECT,
    options: familyOptions,
    selectReturnValue: "value",
  },
  {
    label: i18n.t("data-pages.tools.category"),
    varName: "category",
    type: fieldTypes.TEXT,
  },
  {
    label: i18n.t("data-pages.tools.brand"),
    varName: "brand",
    type: fieldTypes.TEXT,
  },
  {
    label: i18n.t("data-pages.tools.model"),
    varName: "model",
    type: fieldTypes.TEXT,
  },
] as AutoFormItems;

// ============================================================
// Create
const createForm = reactive({
  items: formItems,
  data: { name: "", onHand: false } as RecipeToolCreate,
});

async function handleCreate(createFormData: RecipeToolCreate) {
  // @ts-expect-error createOne eroniusly expects id and slug which are not preset at time of creation
  await toolStore.actions.createOne({
    name: createFormData.name,
    householdsWithTool: createFormData.onHand ? [userHousehold.value] : [],
    family: createFormData.family,
    category: createFormData.category,
    brand: createFormData.brand,
    model: createFormData.model,
  } as RecipeToolCreate);
  createForm.data = { name: "", onHand: false } as RecipeToolCreate;
}

// ============================================================
// Edit
const editForm = reactive({
  items: formItems,
  data: {} as RecipeToolWithOnHand,
});

async function handleEdit(editFormData: RecipeToolWithOnHand) {
  // if list of households is undefined default to empty array
  if (!editFormData.householdsWithTool) {
    editFormData.householdsWithTool = [];
  }

  if (editFormData.onHand && !editFormData.householdsWithTool.includes(userHousehold.value)) {
    editFormData.householdsWithTool.push(userHousehold.value);
  }
  else if (!editFormData.onHand && editFormData.householdsWithTool.includes(userHousehold.value)) {
    const idx = editFormData.householdsWithTool.indexOf(userHousehold.value);
    if (idx !== -1) editFormData.householdsWithTool.splice(idx, 1);
  }

  await toolStore.actions.updateOne({ ...editFormData, id: editFormData.id } as RecipeTool);
  editForm.data = {} as RecipeToolWithOnHand;
}

// ============================================================
// Bulk Actions
async function handleBulkAction(event: string, items: RecipeToolWithOnHand[]) {
  if (event === "delete-selected") {
    const ids = items.filter(item => item.id != null).map(item => item.id!);
    await toolStore.actions.deleteMany(ids);
  }
}

// ============================================================
// Merge Tools
const mergeDialog = ref(false);
const fromTool = ref<RecipeToolWithOnHand | null>(null);
const toTool = ref<RecipeToolWithOnHand | null>(null);

const canMerge = computed(() => {
  return fromTool.value && toTool.value && fromTool.value.id !== toTool.value.id;
});

function resetMergeDialog() {
  fromTool.value = null;
  toTool.value = null;
}

async function mergeTools() {
  if (!canMerge.value || !fromTool.value?.id || !toTool.value?.id) {
    return;
  }

  const { data } = await userApi.tools.merge(fromTool.value.id, toTool.value.id);

  if (data) {
    fromTool.value = null;
    toTool.value = null;
    toolStore.actions.refresh();
  }
}

// ============================================================
// Delete Unused
const DELETE_UNUSED_PREVIEW_LIMIT = 10;

const deleteUnusedDialog = ref(false);
const unusedTools = ref<RecipeTool[]>([]);
const unusedToolIds = computed(() => unusedTools.value.filter(t => t.id != null).map(t => t.id!));
const unusedToolNamesPreview = computed(() => unusedTools.value.slice(0, DELETE_UNUSED_PREVIEW_LIMIT).map(t => t.name));
const unusedToolNamesRemaining = computed(() => Math.max(unusedTools.value.length - DELETE_UNUSED_PREVIEW_LIMIT, 0));
const loadingEmpty = ref(false);

async function openDeleteUnusedDialog() {
  loadingEmpty.value = true;
  const { data } = await userApi.tools.getEmpty();
  loadingEmpty.value = false;
  unusedTools.value = data ?? [];

  if (unusedTools.value.length === 0) {
    alert.info(i18n.t("data-pages.tools.no-unused-tools"));
    return;
  }

  deleteUnusedDialog.value = true;
}

async function confirmDeleteUnused() {
  await toolStore.actions.deleteMany(unusedToolIds.value);
  unusedTools.value = [];
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
  const { data } = await userApi.seeders.tools({ locale: locale.value });

  if (data) {
    toolStore.actions.refresh();
  }
}
</script>
