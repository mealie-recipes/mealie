<template>
  <!-- Create Dialog -->
  <BaseDialog
    v-model="createDialog"
    :title="$t('general.create')"
    :icon="icon"
    color="primary"
    :submit-disabled="!createFormValid"
    can-confirm
    @confirm="emit('create-one', createForm.data)"
  >
    <div class="mx-2 mt-2">
      <AutoForm
        v-model="createForm.data"
        v-model:is-valid="createFormValid"
        :items="createForm.items"
      />
    </div>
  </BaseDialog>

  <!-- Edit Dialog -->
  <BaseDialog
    v-model="editDialog"
    :title="$t('general.edit')"
    :icon="icon"
    color="primary"
    :submit-disabled="!editFormValid"
    can-confirm
    @confirm="emit('edit-one', editForm.data)"
  >
    <div class="mx-2 mt-2">
      <AutoForm
        v-model="editForm.data"
        v-model:is-valid="editFormValid"
        :items="editForm.items"
      />
    </div>
  </BaseDialog>

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
    @edit-one="editEventHandler"
    @delete-one="deleteEventHandler"
    @delete-selected="bulkDeleteEventHandler"
  >
    <template
      v-for="slotName in itemSlotNames"
      #[slotName]="slotProps"
    >
      <slot
        :name="slotName"
        v-bind="slotProps"
      />
    </template>
    <template #button-row>
      <BaseButton
        create
        @click="createDialog = true"
      >
        {{ $t("general.create") }}
      </BaseButton>
    </template>
  </CrudTable>
</template>

<script setup lang="ts">
import type { AutoFormItems } from "~/types/auto-forms";

const slots = useSlots();

export type GroupDataPageTableHeader = {
  text: string;
  value: string;
  show: boolean;
  sortable?: boolean;
};

export type GroupDataPageTableConfig = {
  hideColumns: boolean;
  canExport: boolean;
};

export type GroupDataPageBulkAction = {
  icon: string;
  text: string;
  event: string;
};

const emit = defineEmits<{
  (e: "deleteOne", id: string): void;
  (e: "deleteMany", ids: Array<string>): void;
  (e: "create-one" | "edit-one", data: any): void;
}>();

const tableHeaders = defineModel<Array<GroupDataPageTableHeader>>("tableHeaders", { required: true });
const createForm = defineModel<{ items: AutoFormItems; data: Record<string, any> }>("createForm", { required: true });
const createDialog = defineModel("createDialog", { type: Boolean, default: false });

const editForm = defineModel<{ items: AutoFormItems; data: Record<string, any> }>("editForm", { required: true });
const editDialog = defineModel("editDialog", { type: Boolean, default: false });

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
    type: Object as PropType<GroupDataPageTableConfig>,
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
    type: Array as PropType<Array<GroupDataPageBulkAction>>,
    required: true,
  },
});

// ============================================================
// Create & Edit
const createFormValid = ref(false);
const editFormValid = ref(false);
const itemSlotNames = computed(() => Object.keys(slots).filter(slotName => slotName.startsWith("item.")));
const editEventHandler = (item: any) => {
  editForm.value.data = { ...item };
  editDialog.value = true;
};

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
