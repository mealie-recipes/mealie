<template>
  <v-container>
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="125" max-width="125" :src="require('~/static/svgs/manage-members.svg')"></v-img>
      </template>
      <template #title> Manage Memebers </template>
      Manage the permissions of the members in your groups. <b> Manage </b> allows the user to access the
      data-management page <b> Invite </b> allows the user to generate invitation links for other users. Group owners
      cannot change their own permissions.
    </BasePageTitle>
    <v-data-table
      :headers="headers"
      :items="members || []"
      item-key="id"
      class="elevation-0"
      hide-default-footer
      disable-pagination
    >
      <template #item.avatar="">
        <v-avatar>
          <img src="https://i.pravatar.cc/300" alt="John" />
        </v-avatar>
      </template>
      <template #item.admin="{ item }">
        {{ item.admin ? "Admin" : "User" }}
      </template>
      <template #item.manage="{ item }">
        <div class="d-flex justify-center">
          <v-checkbox
            v-model="item.canManage"
            :disabled="item.id === $auth.user.id || item.admin"
            class=""
            style="max-width: 30px"
            @change="setPermissions(item)"
          ></v-checkbox>
        </div>
      </template>
      <template #item.organize="{ item }">
        <div class="d-flex justify-center">
          <v-checkbox
            v-model="item.canOrganize"
            :disabled="item.id === $auth.user.id || item.admin"
            class=""
            style="max-width: 30px"
            @change="setPermissions(item)"
          ></v-checkbox>
        </div>
      </template>
      <template #item.invite="{ item }">
        <div class="d-flex justify-center">
          <v-checkbox
            v-model="item.canInvite"
            :disabled="item.id === $auth.user.id || item.admin"
            class=""
            style="max-width: 30px"
            @change="setPermissions(item)"
          ></v-checkbox>
        </div>
      </template>
    </v-data-table>
  </v-container>
</template>
    
<script lang="ts">
import { defineComponent, ref, onMounted, useContext } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { UserOut } from "~/types/api-types/user";

export default defineComponent({
  setup() {
    const api = useUserApi();

    const { i18n } = useContext();

    const members = ref<UserOut[] | null[]>([]);

    const headers = [
      { text: "", value: "avatar", sortable: false, align: "center" },
      { text: i18n.t("user.username"), value: "username" },
      { text: i18n.t("user.full-name"), value: "fullName" },
      { text: i18n.t("user.admin"), value: "admin" },
      { text: "Manage", value: "manage", sortable: false, align: "center" },
      { text: "Organize", value: "organize", sortable: false, align: "center" },
      { text: "Invite", value: "invite", sortable: false, align: "center" },
    ];

    async function refreshMembers() {
      const { data } = await api.groups.fetchMembers();
      if (data) {
        members.value = data;
      }
    }

    async function setPermissions(user: UserOut) {
      const payload = {
        userId: user.id,
        canInvite: user.canInvite,
        canManage: user.canManage,
        canOrganize: user.canOrganize,
      };

      await api.groups.setMemberPermissions(payload);
    }

    onMounted(async () => {
      await refreshMembers();
    });

    return { members, headers, setPermissions };
  },
  head() {
    return {
      title: "Members",
    };
  },
});
</script>