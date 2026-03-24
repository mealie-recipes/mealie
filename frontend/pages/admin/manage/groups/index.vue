<template>
  <v-container fluid>
    <BaseDialog
      v-model="state.createDialog"
      :title="$t('group.create-group')"
      :icon="$globals.icons.group"
      can-submit
      @submit="createGroup(state.createGroupForm.data)"
    >
      <template #activator />
      <v-card-text>
        <AutoForm
          v-model="state.createGroupForm.data"
          :update-mode="state.updateMode"
          :items="state.createGroupForm.items"
        />
      </v-card-text>
    </BaseDialog>

    <BaseDialog
      v-model="state.confirmDialog"
      :title="$t('general.confirm')"
      color="error"
      can-confirm
      @confirm="deleteGroup(state.deleteTarget)"
    >
      <template #activator />
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
      </v-card-text>
    </BaseDialog>

    <BaseCardSectionTitle :title="$t('group.group-management')" />
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
        :headers="state.headers"
        :items="groups || []"
        item-key="id"
        class="elevation-0"
        :items-per-page="-1"
        hide-default-footer
        disable-pagination
        :search="state.search"
        @click:row="($event, { item }) => handleRowClick(item)"
      >
        <template #[`item.households`]="{ item }">
          {{ item.households!.length }}
        </template>
        <template #[`item.users`]="{ item }">
          {{ item.users!.length }}
        </template>
        <template #[`item.actions`]="{ item }">
          <v-tooltip
            location="bottom"
            :disabled="!(item && (item.households!.length > 0 || item.users!.length > 0))"
          >
            <template #activator="{ props }">
              <div v-bind="props">
                <v-btn
                  :disabled="item && (item.households!.length > 0 || item.users!.length > 0)"
                  class="mr-1"
                  icon
                  color="error"
                  variant="text"
                  @click.stop="
                    state.confirmDialog = true;
                    state.deleteTarget = item.id;
                  "
                >
                  <v-icon>
                    {{ $globals.icons.delete }}
                  </v-icon>
                </v-btn>
              </div>
            </template>
            <span>{{ $t("admin.group-delete-note") }}</span>
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
import { validators } from "~/composables/use-validators";
import type { GroupInDB } from "~/lib/api/types/user";

definePageMeta({
  layout: "admin",
});

const i18n = useI18n();

useHead({
  title: i18n.t("group.manage-groups"),
});

// Set page title
useSeoMeta({
  title: i18n.t("group.manage-groups"),
});

const { groups, deleteGroup, createGroup } = useGroups();

const state = reactive({
  createDialog: false,
  confirmDialog: false,
  deleteTarget: "",
  search: "",
  headers: [
    {
      title: i18n.t("group.group"),
      align: "start",
      sortable: false,
      value: "id",
    },
    { title: i18n.t("general.name"), value: "name" },
    { title: i18n.t("group.total-households"), value: "households" },
    { title: i18n.t("user.total-users"), value: "users" },
    { title: i18n.t("general.delete"), value: "actions" },
  ],
  updateMode: false,
  createGroupForm: {
    items: [
      {
        label: i18n.t("group.group-name"),
        varName: "name",
        type: fieldTypes.TEXT,
        rules: [validators.required],
      },
    ],
    data: {
      name: "",
    },
  },
});

function openDialog() {
  state.createDialog = true;
  state.createGroupForm.data.name = "";
}

function handleRowClick(item: GroupInDB) {
  navigateTo(`/admin/manage/groups/${item.id}`);
}
</script>
