<template>
  <v-container fluid>
    <BaseDialog
      v-model="createDialog"
      :title="$t('group.create-group')"
      :icon="$globals.icons.group"
      @submit="createGroup(createGroupForm.data)"
    >
      <template #activator> </template>
      <v-card-text>
        <AutoForm v-model="createGroupForm.data" :update-mode="updateMode" :items="createGroupForm.items" />
      </v-card-text>
    </BaseDialog>

    <BaseDialog
      v-model="confirmDialog"
      :title="$t('general.confirm')"
      color="error"
      @confirm="deleteGroup(deleteTarget)"
    >
      <template #activator> </template>
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
      </v-card-text>
    </BaseDialog>

    <BaseCardSectionTitle :title="$tc('group.group-management')"> </BaseCardSectionTitle>
    <section>
      <v-toolbar flat color="transparent" class="justify-between">
        <BaseButton @click="openDialog"> {{ $t("general.create") }} </BaseButton>
      </v-toolbar>

      <v-data-table
        :headers="headers"
        :items="groups || []"
        item-key="id"
        class="elevation-0"
        hide-default-footer
        disable-pagination
        :search="search"
        @click:row="handleRowClick"
      >
        <template #item.households="{ item }">
          {{ item.households.length }}
        </template>
        <template #item.users="{ item }">
          {{ item.users.length }}
        </template>
        <template #item.actions="{ item }">
          <v-tooltip bottom :disabled="!(item && (item.households.length > 0 || item.users.length > 0))">
            <template #activator="{ on, attrs }">
              <div v-bind="attrs" v-on="on" >
                <v-btn
                  :disabled="item && (item.households.length > 0 || item.users.length > 0)"
                  class="mr-1"
                  icon
                  color="error"
                  @click.stop="
                    confirmDialog = true;
                    deleteTarget = item.id;
                  "
                >
                  <v-icon>
                    {{ $globals.icons.delete }}
                  </v-icon>
                </v-btn>
              </div>
            </template>
            <span>{{ $tc("admin.group-delete-note") }}</span>
          </v-tooltip>
        </template>
      </v-data-table>
      <v-divider></v-divider>
    </section>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, useContext, useRouter } from "@nuxtjs/composition-api";
import { fieldTypes } from "~/composables/forms";
import { useGroups } from "~/composables/use-groups";
import { GroupInDB } from "~/lib/api/types/user";

export default defineComponent({
  layout: "admin",
  setup() {
    const { i18n } = useContext();
    const { groups, refreshAllGroups, deleteGroup, createGroup } = useGroups();

    const state = reactive({
      createDialog: false,
      confirmDialog: false,
      deleteTarget: 0,
      search: "",
      headers: [
        {
          text: i18n.t("group.group"),
          align: "start",
          sortable: false,
          value: "id",
        },
        { text: i18n.t("general.name"), value: "name" },
        { text: i18n.t("group.total-households"), value: "households" },
        { text: i18n.t("user.total-users"), value: "users" },
        { text: i18n.t("general.delete"), value: "actions" },
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

    const router = useRouter();

    function handleRowClick(item: GroupInDB) {
      router.push(`/admin/manage/groups/${item.id}`);
    }

    return { ...toRefs(state), groups, refreshAllGroups, deleteGroup, createGroup, openDialog, handleRowClick };
  },
  head() {
    return {
      title: this.$t("group.manage-groups") as string,
    };
  },
});
</script>
