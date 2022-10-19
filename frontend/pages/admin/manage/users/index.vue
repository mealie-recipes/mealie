<template>
  <v-container fluid>
    <BaseDialog v-model="deleteDialog" :title="$t('general.confirm')" color="error" @confirm="deleteUser(deleteTarget)">
      <template #activator> </template>
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
      </v-card-text>
    </BaseDialog>

    <BaseCardSectionTitle title="User Management"> </BaseCardSectionTitle>
    <section>
      <v-toolbar color="background" flat class="justify-between">
        <BaseButton to="/admin/manage/users/create" class="mr-2">
          {{ $t("general.create") }}
        </BaseButton>

        <BaseOverflowButton
          mode="event"
          :items="[
            {
              text: 'Reset Locked Users',
              icon: $globals.icons.lock,
              event: 'unlock-all-users',
            },
          ]"
          @unlock-all-users="unlockAllUsers"
        >
        </BaseOverflowButton>
      </v-toolbar>
      <v-data-table
        :headers="headers"
        :items="users || []"
        item-key="id"
        class="elevation-0"
        elevation="0"
        hide-default-footer
        disable-pagination
        :search="search"
        @click:row="handleRowClick"
      >
        <template #item.admin="{ item }">
          <v-icon right :color="item.admin ? 'success' : null">
            {{ item.admin ? $globals.icons.checkboxMarkedCircle : $globals.icons.windowClose }}
          </v-icon>
        </template>
        <template #item.actions="{ item }">
          <v-btn
            icon
            :disabled="item.id == 1"
            color="error"
            @click.stop="
              deleteDialog = true;
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
import { defineComponent, reactive, ref, toRefs, useContext, useRouter } from "@nuxtjs/composition-api";
import { useAdminApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { useUser, useAllUsers } from "~/composables/use-user";
import { UserOut } from "~/lib/api/types/user";

export default defineComponent({
  layout: "admin",
  setup() {
    const api = useAdminApi();
    const refUserDialog = ref();

    const { i18n } = useContext();

    const router = useRouter();

    const state = reactive({
      deleteDialog: false,
      deleteTarget: 0,
      search: "",
    });

    const { users, refreshAllUsers } = useAllUsers();
    const { loading, deleteUser } = useUser(refreshAllUsers);

    function handleRowClick(item: UserOut) {
      router.push(`/admin/manage/users/${item.id}`);
    }

    // ==========================================================
    // Constants / Non-reactive

    const headers = [
      {
        text: i18n.t("user.user-id"),
        align: "start",
        value: "id",
      },
      { text: i18n.t("user.username"), value: "username" },
      { text: i18n.t("user.full-name"), value: "fullName" },
      { text: i18n.t("user.email"), value: "email" },
      { text: i18n.t("group.group"), value: "group" },
      { text: i18n.t("user.admin"), value: "admin" },
      { text: i18n.t("general.delete"), value: "actions", sortable: false, align: "center" },
    ];

    async function unlockAllUsers(): Promise<void> {
      const { data } = await api.users.unlockAllUsers(true);

      if (data) {
        const unlocked = data.unlocked ?? 0;

        alert.success(`${unlocked} user(s) unlocked`);
        refreshAllUsers();
      }
    }

    return {
      unlockAllUsers,
      ...toRefs(state),
      headers,
      deleteUser,
      loading,
      refUserDialog,
      users,
      handleRowClick,
    };
  },
  head() {
    return {
      title: this.$t("sidebar.manage-users") as string,
    };
  },
});
</script>
