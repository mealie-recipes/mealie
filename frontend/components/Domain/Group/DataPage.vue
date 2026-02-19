<template>
  <!-- Delete Dialog -->
  <BaseDialog
    v-model="deleteDialog"
    :title="$t('general.confirm')"
    :icon="$globals.icons.alertCircle"
    color="error"
    can-confirm
    @confirm="$emit('deleteOne', deleteTarget.id)"
  >
    <v-card-text>
      {{ $t("general.confirm-delete-generic") }}
      <p v-if="deleteTarget" class="mt-4 ml-4">
        {{ deleteTarget.name }}
      </p>
    </v-card-text>
  </BaseDialog>

  <!-- Bulk Delete Dialog -->
  <BaseDialog
    v-model="bulkDeleteDialog"
    width="650px"
    :title="$t('general.confirm')"
    :icon="$globals.icons.alertCircle"
    color="error"
    can-confirm
    @confirm="$emit('deleteMany', bulkDeleteTarget.map((item) => item.id))"
  >
    <v-card-text>
      <p class="h4">
        {{ $t('general.confirm-delete-generic-items') }}
      </p>
      <v-card variant="outlined">
        <v-virtual-scroll height="400" item-height="25" :items="bulkDeleteTarget">
          <template #default="{ item }">
            <v-list-item class="pb-2">
              <v-list-item-title>{{ item.name }}</v-list-item-title>
            </v-list-item>
          </template>
        </v-virtual-scroll>
      </v-card>
    </v-card-text>
  </BaseDialog>

  <BaseCardSectionTitle
    :icon="icon"
    section
    :title="title"
  />

  <CrudTable
    v-model:headers="tableHeaders"
    :table-config="tableConfig"
    :data="data || []"
    :bulk-actions="bulkActions"
    initial-sort="name"
    @delete-one="deleteEventHandler"
    @delete-selected="bulkDeleteEventHandler"
  >
    <template #button-row>
      <BaseButton
        create
        @click="state.createDialog = true"
      >
        {{ $t("general.create") }}
      </BaseButton>
    </template>
  </CrudTable>
</template>

<script setup lang="ts">
export type DataPageTableHeader = {
  text: string;
  value: string;
  show: boolean;
  sortable?: boolean;
};

export type DataPageTableConfig = {
  hideColumns: boolean;
  canExport: boolean;
};

export type DataPageBulkAction = {
  icon: string;
  text: string;
  event: string;
};

defineEmits<{
  (e: "deleteOne", id: string): void;
  (e: "deleteMany", ids: Array<string>): void;
}>();

const tableHeaders = defineModel<Array<DataPageTableHeader>>("tableHeaders", { required: true });

defineProps({
  icon: {
    type: String,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  tableConfig: {
    type: Object as PropType<DataPageTableConfig>,
    default: () => ({
      hideColumns: false,
      canExport: true,
    }),
  },
  data: {
    type: Array as PropType<Array<any>>,
    required: true,
  },
  bulkActions: {
    type: Array as PropType<Array<DataPageBulkAction>>,
    required: true,
  },
});

// ============================================================
// Delete Logic
const deleteTarget = ref<any>(null);
const deleteDialog = ref(false);

function deleteEventHandler(item: any) {
  deleteTarget.value = item;
  deleteDialog.value = true;
}

// ============================================================
// Bulk Delete Logic
const bulkDeleteTarget = ref<Array<any>>([]);
const bulkDeleteDialog = ref(false);

function bulkDeleteEventHandler(items: Array<any>) {
  bulkDeleteTarget.value = items;
  bulkDeleteDialog.value = true;
  console.log("Bulk Delete Event Handler", items);
}
</script>
