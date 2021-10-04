// TODO: Edit User 
<template>
  <v-container fluid>
    <BaseCardSectionTitle title="User Management"> </BaseCardSectionTitle>
    <section>
      <v-toolbar color="background" flat class="justify-between">
        <BaseDialog
          ref="refUserDialog"
          top
          :title="$t('user.create-user')"
          @submit="createUser(createUserForm.data)"
          @close="resetForm"
        >
          <template #activator="{ open }">
            <BaseButton @click="open"> {{ $t("user.create-user") }} </BaseButton>
          </template>
          <v-card-text>
            <v-select
              v-model="createUserForm.data.group"
              :items="groups"
              rounded
              class="rounded-lg"
              item-text="name"
              item-value="name"
              :return-object="false"
              filled
              label="Filled style"
            ></v-select>
            <AutoForm v-model="createUserForm.data" :update-mode="updateMode" :items="createUserForm.items" />
          </v-card-text>
        </BaseDialog>
      </v-toolbar>
      <v-data-table
        :headers="headers"
        :items="users || []"
        item-key="id"
        class="elevation-0"
        hide-default-footer
        disable-pagination
        :search="search"
      >
        <template #item.admin="{ item }">
          {{ item.admin ? "Admin" : "User" }}
        </template>
        <template #item.actions="{ item }">
          <BaseDialog :title="$t('general.confirm')" color="error" @confirm="deleteUser(item.id)">
            <template #activator="{ open }">
              <v-btn :disabled="item.id == 1" class="mr-1" small color="error" @click="open">
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
import { defineComponent, ref } from "@nuxtjs/composition-api";
import { fieldTypes } from "~/composables/forms";
import { useApiSingleton } from "~/composables/use-api";
import { useGroups } from "~/composables/use-groups";
import { useUser, useAllUsers } from "~/composables/use-user";

export default defineComponent({
  layout: "admin",
  setup() {
    const api = useApiSingleton();
    const refUserDialog = ref();

    const { groups } = useGroups();

    const { users, refreshAllUsers } = useAllUsers();
    const { loading, getUser, deleteUser, createUser } = useUser(refreshAllUsers);

    return { refUserDialog, api, users, deleteUser, createUser, getUser, loading, groups };
  },
  data() {
    return {
      search: "",
      headers: [
        {
          text: this.$t("user.user-id"),
          align: "start",
          sortable: false,
          value: "id",
        },
        { text: this.$t("user.username"), value: "username" },
        { text: this.$t("user.full-name"), value: "fullName" },
        { text: this.$t("user.email"), value: "email" },
        { text: this.$t("group.group"), value: "group" },
        { text: this.$t("user.admin"), value: "admin" },
        { text: "", value: "actions", sortable: false, align: "center" },
      ],
      updateMode: false,
      createUserForm: {
        items: [
          {
            label: "User Name",
            varName: "username",
            type: fieldTypes.TEXT,
            rules: ["required"],
          },
          {
            label: "Full Name",
            varName: "fullName",
            type: fieldTypes.TEXT,
            rules: ["required"],
          },
          {
            label: "Email",
            varName: "email",
            type: fieldTypes.TEXT,
            rules: ["required"],
          },
          {
            label: "Passord",
            varName: "password",
            fixed: true,
            type: fieldTypes.TEXT,
            rules: ["required"],
          },
          {
            label: "Administrator",
            varName: "admin",
            type: fieldTypes.BOOLEAN,
            rules: ["required"],
          },
        ],
        data: {
          username: "",
          fullName: "",
          email: "",
          admin: false,
          group: "",
          favoriteRecipes: [],
          password: "",
        },
      },
    };
  },
  methods: {
    updateUser(userData: any) {
      this.updateMode = true;
      this.createUserForm.data = userData;
      this.refUserDialog.open();
    },
    resetForm() {
      this.createUserForm.data = {
        username: "",
        fullName: "",
        email: "",
        admin: false,
        group: "",
        favoriteRecipes: [],
        password: "",
      };
    },
  },
});
</script>

<style scoped>
</style>