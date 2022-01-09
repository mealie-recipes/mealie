// TODO: Edit Group
<template>
  <v-container fluid>
    <BaseDialog
      v-model="createDialog"
      :title="$t('group.create-group')"
      :icon="$globals.icons.group"
      @submit="createGroup(createUserForm.data)"
    >
      <template #activator> </template>
      <v-card-text>
        <AutoForm v-model="createUserForm.data" :update-mode="updateMode" :items="createUserForm.items" />
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

    <BaseCardSectionTitle title="Group Management"> </BaseCardSectionTitle>
    <section>
      <v-toolbar flat color="background" class="justify-between">
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
        <template #item.shoppingLists="{ item }">
          {{ item.shoppingLists.length }}
        </template>
        <template #item.users="{ item }">
          {{ item.users.length }}
        </template>
        <template #item.webhookEnable="{ item }">
          {{ item.webhooks.length > 0 ? $t("general.yes") : $t("general.no") }}
        </template>
        <template #item.actions="{ item }">
          <v-btn
            :disabled="item && item.users.length > 0"
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
        </template>
      </v-data-table>
      <v-divider></v-divider>
    </section>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, useContext, useRouter } from "@nuxtjs/composition-api";
import { Group } from "~/api/class-interfaces/groups";
import { fieldTypes } from "~/composables/forms";
import { useGroups } from "~/composables/use-groups";

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
        { text: i18n.t("user.total-users"), value: "users" },
        { text: i18n.t("user.webhooks-enabled"), value: "webhookEnable" },
        { text: i18n.t("shopping-list.shopping-lists"), value: "shoppingLists" },
        { text: i18n.t("general.delete"), value: "actions" },
      ],
      updateMode: false,
      createUserForm: {
        items: [
          {
            label: "Group Name",
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
      state.createUserForm.data.name = "";
    }

    const router = useRouter();

    function handleRowClick(item: Group) {
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
