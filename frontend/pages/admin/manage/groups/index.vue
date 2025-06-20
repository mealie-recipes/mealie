<template>
  <v-container fluid>
    <BaseDialog
      v-model="createDialog"
      :title="$t('group.create-group')"
      :icon="$globals.icons.group"
      can-submit
      @submit="createGroup(createGroupForm.data)"
    >
      <template #activator />
      <v-card-text>
        <AutoForm
          v-model="createGroupForm.data"
          :update-mode="updateMode"
          :items="createGroupForm.items"
        />
      </v-card-text>
    </BaseDialog>

    <BaseDialog
      v-model="confirmDialog"
      :title="$t('general.confirm')"
      color="error"
      can-confirm
      @confirm="deleteGroup(deleteTarget)"
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
        :headers="headers"
        :items="groups || []"
        item-key="id"
        class="elevation-0"
        hide-default-footer
        disable-pagination
        :search="search"
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
            bottom
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
                    confirmDialog = true;
                    deleteTarget = +item.id;
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

<script lang="ts">
import { fieldTypes } from "~/composables/forms";
import { useGroups } from "~/composables/use-groups";
import type { GroupInDB } from "~/lib/api/types/user";

export default defineNuxtComponent({
  setup() {
    definePageMeta({
      layout: "admin",
    });

    const i18n = useI18n();

    // Set page title
    useSeoMeta({
      title: i18n.t("group.manage-groups"),
    });

    const { groups, refreshAllGroups, deleteGroup, createGroup } = useGroups();

    const state = reactive({
      createDialog: false,
      confirmDialog: false,
      deleteTarget: 0,
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
            rules: ["required"],
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

    return { ...toRefs(state), groups, refreshAllGroups, deleteGroup, createGroup, openDialog, handleRowClick };
  },
  head() {
    return {
      title: useI18n().t("group.manage-groups"),
    };
  },
});
</script>
