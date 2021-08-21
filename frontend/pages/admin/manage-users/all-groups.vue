// TODO: Edit Group
<template>
  <v-container fluid>
    <BaseCardSectionTitle title="Group Management"> </BaseCardSectionTitle>
    <section>
      <v-toolbar flat class="justify-between">
        <BaseDialog
          ref="refUserDialog"
          top
          :title="$t('group.create-group')"
          @submit="createGroup(createUserForm.data)"
        >
          <template #activator="{ open }">
            <BaseButton @click="open"> {{ $t("group.create-group") }} </BaseButton>
          </template>
          <v-card-text>
            <AutoForm v-model="createUserForm.data" :update-mode="updateMode" :items="createUserForm.items" />
          </v-card-text>
        </BaseDialog>
      </v-toolbar>
      <v-data-table
        :headers="headers"
        :items="groups || []"
        item-key="id"
        class="elevation-0"
        hide-default-footer
        disable-pagination
        :search="search"
      >
        <template #item.mealplans="{ item }">
          {{ item.mealplans.length }}
        </template>
        <template #item.shoppingLists="{ item }">
          {{ item.shoppingLists.length }}
        </template>
        <template #item.users="{ item }">
          {{ item.users.length }}
        </template>
        <template #item.webhookEnable="{ item }">
          {{ item.webhookEnabled ? $t("general.yes") : $t("general.no") }}
        </template>
        <template #item.actions="{ item }">
          <BaseDialog :title="$t('general.confirm')" color="error" @confirm="deleteGroup(item.id)">
            <template #activator="{ open }">
              <v-btn :disabled="item && item.users.length > 0" class="mr-1" small color="error" @click="open">
                <v-icon small left>
                  {{ $globals.icons.delete }}
                </v-icon>
                {{ $t("general.delete") }}
              </v-btn>
              <v-btn small color="success" @click="updateUser(item)">
                <v-icon small left class="mr-2">
                  {{ $globals.icons.edit }}
                </v-icon>
                {{ $t("general.edit") }}
              </v-btn>
            </template>
            <v-card-text>
              {{ $t("general.confirm-delete-generic") }}
            </v-card-text>
          </BaseDialog>
        </template>
      </v-data-table>
      <v-divider></v-divider>
    </section>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, useContext } from "@nuxtjs/composition-api";
import { fieldTypes } from "~/composables/forms";
import { useGroups } from "~/composables/use-groups";

export default defineComponent({
  layout: "admin",
  setup() {
    const { i18n } = useContext();
    const { groups, refreshAllGroups, deleteGroup, createGroup } = useGroups();

    const state = reactive({
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
        { text: i18n.t("user.total-mealplans"), value: "mealplans" },
        { text: i18n.t("shopping-list.shopping-lists"), value: "shoppingLists" },
        { value: "actions" },
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

    return { ...toRefs(state), groups, refreshAllGroups, deleteGroup, createGroup };
  },
});
</script>
