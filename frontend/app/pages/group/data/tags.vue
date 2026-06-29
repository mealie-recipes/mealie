<template>
  <div>
    <BaseDialog
      v-model="deleteUnusedDialog"
      :title="$t('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      can-confirm
      @confirm="confirmDeleteUnused"
    >
      <v-card-text>
        Delete {{ unusedTagIds.length }} unused tag(s)? This cannot be undone.
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
        <NuxtLink :to="`/g/${groupSlug}?tags=${item.id}`">{{ item.recipeCount }}</NuxtLink>
      </template>

      <template #table-button-row>
        <BaseButton :loading="loadingEmpty" @click="openDeleteUnusedDialog">
          <template #icon>
            {{ $globals.icons.delete }}
          </template>
          Delete Unused
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
    text: "Recipe Count",
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
// Delete Unused
const deleteUnusedDialog = ref(false);
const unusedTagIds = ref<string[]>([]);
const loadingEmpty = ref(false);

async function openDeleteUnusedDialog() {
  loadingEmpty.value = true;
  const { data } = await userApi.tags.getEmpty();
  loadingEmpty.value = false;
  unusedTagIds.value = (data ?? []).filter(t => t.id != null).map(t => t.id!);
  deleteUnusedDialog.value = true;
}

async function confirmDeleteUnused() {
  await tagStore.actions.deleteMany(unusedTagIds.value);
  unusedTagIds.value = [];
}
</script>
