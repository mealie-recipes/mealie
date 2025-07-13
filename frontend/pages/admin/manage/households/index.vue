<template>
  <v-container fluid>
    <BaseDialog
      v-model="createDialog"
      :title="$t('household.create-household')"
      :icon="$globals.icons.household"
    >
      <template #activator />
      <v-card-text>
        <v-form ref="refNewHouseholdForm">
          <v-select
            v-if="groups"
            v-model="createHouseholdForm.data.groupId"
            :items="groups"
            item-title="name"
            item-value="id"
            variant="filled"
            :label="$t('household.household-group')"
            :rules="[validators.required]"
          />
          <AutoForm
            v-model="createHouseholdForm.data"
            :update-mode="updateMode"
            :items="createHouseholdForm.items"
          />
        </v-form>
      </v-card-text>
      <template #custom-card-action>
        <BaseButton
          type="submit"
          @click="handleCreateSubmit"
        >
          {{ $t("general.create") }}
        </BaseButton>
      </template>
    </BaseDialog>

    <BaseDialog
      v-model="confirmDialog"
      :title="$t('general.confirm')"
      color="error"
      can-confirm
      @confirm="deleteHousehold(deleteTarget)"
    >
      <template #activator />
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
      </v-card-text>
    </BaseDialog>

    <BaseCardSectionTitle :title="$t('household.household-management')" />
    <section>
      <v-toolbar
        flat
        color="transparent"
        class="justify-between"
      >
        <BaseButton @click="openDialog">
          {{ $t("general.create") }}
        </BaseButton>
      </v-toolbar>

      <v-data-table
        v-if="headers && households"
        :headers="headers"
        :items="households"
        item-key="id"
        class="elevation-0"
        hide-default-footer
        disable-pagination
        :search="search"
        @click:row="($event, { item }) => handleRowClick(item)"
      >
        <template #[`item.users`]="{ item }">
          {{ item.users?.length }}
        </template>
        <template #[`item.group`]="{ item }">
          {{ item.group }}
        </template>
        <template #[`item.webhookEnable`]="{ item }">
          {{ item.webhooks!.length > 0 ? $t("general.yes") : $t("general.no") }}
        </template>
        <template #[`item.actions`]="{ item }">
          <v-tooltip
            bottom
            :disabled="!(item && item.users!.length > 0)"
          >
            <template #activator="{ props }">
              <div v-bind="props">
                <v-btn
                  :disabled="item && item.users!.length > 0"
                  class="mr-1"
                  icon
                  color="error"
                  variant="text"
                  @click.stop="confirmDialog = true; deleteTarget = item.id"
                >
                  <v-icon>
                    {{ $globals.icons.delete }}
                  </v-icon>
                </v-btn>
              </div>
            </template>
            <span>{{ $t("admin.household-delete-note") }}</span>
          </v-tooltip>
        </template>
      </v-data-table>
      <v-divider />
    </section>
  </v-container>
</template>

<script setup lang="ts">
import { fieldTypes } from "~/composables/forms";
import { useGroups } from "~/composables/use-groups";
import { useAdminHouseholds } from "~/composables/use-households";
import { validators } from "~/composables/use-validators";
import type { HouseholdInDB } from "~/lib/api/types/household";
import type { VForm } from "~/types/auto-forms";

definePageMeta({
  layout: "admin",
});

const i18n = useI18n();

useSeoMeta({
  title: i18n.t("household.manage-households"),
});

const { groups } = useGroups();
const { households, deleteHousehold, createHousehold } = useAdminHouseholds();

const refNewHouseholdForm = ref<VForm | null>(null);

const createDialog = ref(false);
const confirmDialog = ref(false);
const deleteTarget = ref<string>("");
const search = ref("");
const updateMode = ref(false);

const headers = [
  {
    title: i18n.t("household.household"),
    align: "start",
    sortable: false,
    value: "id",
  },
  { title: i18n.t("general.name"), value: "name" },
  { title: i18n.t("group.group"), value: "group" },
  { title: i18n.t("user.total-users"), value: "users" },
  { title: i18n.t("user.webhooks-enabled"), value: "webhookEnable" },
  { title: i18n.t("general.delete"), value: "actions" },
];

const createHouseholdForm = reactive({
  items: [
    {
      label: i18n.t("household.household-name"),
      varName: "name",
      type: fieldTypes.TEXT,
      rules: ["required"],
    },
  ],
  data: {
    groupId: "",
    name: "",
  },
});

function openDialog() {
  createDialog.value = true;
  createHouseholdForm.data.name = "";
  createHouseholdForm.data.groupId = "";
}

const router = useRouter();

function handleRowClick(item: HouseholdInDB) {
  router.push(`/admin/manage/households/${item.id}`);
}

async function handleCreateSubmit() {
  if (!refNewHouseholdForm.value?.validate()) {
    return;
  }
  createDialog.value = false;
  await createHousehold(createHouseholdForm.data);
}
</script>
