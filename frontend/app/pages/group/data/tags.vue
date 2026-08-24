<template>
  <div>
    <!-- Merge Dialog -->
    <BaseDialog
      v-model="mergeDialog"
      :icon="$globals.icons.tags"
      :title="$t('data-pages.tags.combine-tag')"
      can-confirm
      @confirm="mergeTags"
    >
      <v-card-text>
        <div>
          {{ $t("data-pages.tags.merge-dialog-text") }}
        </div>
        <v-autocomplete
          v-model="fromTag"
          return-object
          :items="tagStore.store.value"
          :custom-filter="normalizeFilter"
          item-title="name"
          :label="$t('data-pages.tags.source-tag')"
        />
        <v-autocomplete
          v-model="toTag"
          return-object
          :items="tagStore.store.value"
          :custom-filter="normalizeFilter"
          item-title="name"
          :label="$t('data-pages.tags.target-tag')"
        />

        <template v-if="canMerge && fromTag && toTag">
          <div class="text-center">
            {{ $t("data-pages.tags.merge-tag-example", { tag1: fromTag.name, tag2: toTag.name }) }}
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
        {{ $t('data-pages.tags.delete-unused-confirm', { count: unusedTagIds.length }, unusedTagIds.length) }}
        <ul style="margin: 0.5rem 0 0; padding-left: 1.25rem; font-size: 0.85rem; color: rgba(var(--v-theme-on-surface), 0.7); line-height: 1.8;">
          <li v-for="name in unusedTagNamesPreview" :key="name">
            {{ name }}
          </li>
        </ul>
        <div v-if="unusedTagNamesRemaining > 0" class="text-body-2 pl-2">
          {{ $t('data-pages.delete-unused-more', { count: unusedTagNamesRemaining }) }}
        </div>
      </v-card-text>
    </BaseDialog>

    <GroupDataPage
      :icon="$globals.icons.tags"
      :title="$t('data-pages.tags.tag-data')"
      :create-title="$t('data-pages.tags.new-tag')"
      :edit-title="$t('data-pages.tags.edit-tag')"
      :table-headers="tableHeaders"
      :table-config="tableConfig"
      :data="tagStore.store.value || []"
      :bulk-actions="[{ icon: $globals.icons.delete, text: $t('general.delete'), event: 'delete-selected' }]"
      :create-form="createForm"
      :edit-form="editForm"
      @create-one="handleCreate"
      @edit-one="handleEdit"
      @delete-one="tagStore.actions.deleteOne"
      @bulk-action="handleBulkAction"
    >
      <template #[`item.recipeCount`]="{ item }">
        <NuxtLink v-if="groupSlug && item.recipeCount > 0" :to="`/g/${groupSlug}?tags=${item.id}`">{{ item.recipeCount }}</NuxtLink>
        <span v-else>{{ item.recipeCount || 0 }}</span>
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
    </GroupDataPage>
  </div>
</template>

<script setup lang="ts">
import { validators } from "~/composables/use-validators";
import { useTagStore } from "~/composables/store";
import { useUserApi } from "~/composables/api";
import { fieldTypes } from "~/composables/forms";
import { normalizeFilter } from "~/composables/use-utils";
import { alert } from "~/composables/use-toast";
import type { AutoFormItems } from "~/types/auto-forms";
import type { RecipeTag } from "~/lib/api/types/recipe";
import type { TableHeaders, TableConfig } from "~/components/global/CrudTable.vue";

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
];
const tagStore = useTagStore();

// ============================================================
// Form items (shared)
const formItems = [
  {
    label: i18n.t("general.name"),
    varName: "name",
    type: fieldTypes.TEXT,
    rules: [validators.required],
  },
] as AutoFormItems;

// ============================================================
// Create
const createForm = reactive({
  items: formItems,
  data: { name: "" } as RecipeTag,
});

async function handleCreate(createFormData: RecipeTag) {
  await tagStore.actions.createOne(createFormData);
  createForm.data.name = "";
}

// ============================================================
// Edit
const editForm = reactive({
  items: formItems,
  data: {} as RecipeTag,
});

async function handleEdit(editFormData: RecipeTag) {
  await tagStore.actions.updateOne(editFormData);
  editForm.data = {} as RecipeTag;
}

// ============================================================
// Bulk Actions
async function handleBulkAction(event: string, items: RecipeTag[]) {
  if (event === "delete-selected") {
    const ids = items.filter(item => item.id != null).map(item => item.id!);
    await tagStore.actions.deleteMany(ids);
  }
}

// ============================================================
// Merge Tags
const mergeDialog = ref(false);
const fromTag = ref<RecipeTag | null>(null);
const toTag = ref<RecipeTag | null>(null);

const canMerge = computed(() => {
  return fromTag.value && toTag.value && fromTag.value.id !== toTag.value.id;
});

async function mergeTags() {
  if (!canMerge.value || !fromTag.value?.id || !toTag.value?.id) {
    return;
  }

  const { data } = await userApi.tags.merge(fromTag.value.id, toTag.value.id);

  if (data) {
    fromTag.value = null;
    toTag.value = null;
    tagStore.actions.refresh();
  }
}

// ============================================================
// Delete Unused
const DELETE_UNUSED_PREVIEW_LIMIT = 10;

const deleteUnusedDialog = ref(false);
const unusedTags = ref<RecipeTag[]>([]);
const unusedTagIds = computed(() => unusedTags.value.filter(t => t.id != null).map(t => t.id!));
const unusedTagNamesPreview = computed(() => unusedTags.value.slice(0, DELETE_UNUSED_PREVIEW_LIMIT).map(t => t.name));
const unusedTagNamesRemaining = computed(() => Math.max(unusedTags.value.length - DELETE_UNUSED_PREVIEW_LIMIT, 0));
const loadingEmpty = ref(false);

async function openDeleteUnusedDialog() {
  loadingEmpty.value = true;
  const { data } = await userApi.tags.getEmpty();
  loadingEmpty.value = false;
  unusedTags.value = data ?? [];

  if (unusedTags.value.length === 0) {
    alert.info(i18n.t("data-pages.tags.no-unused-tags"));
    return;
  }

  deleteUnusedDialog.value = true;
}

async function confirmDeleteUnused() {
  await tagStore.actions.deleteMany(unusedTagIds.value);
  unusedTags.value = [];
}
</script>
