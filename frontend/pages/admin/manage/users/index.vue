<template>
  <v-container fluid>
    <UserInviteDialog v-model="inviteDialog" />
    <BaseDialog
      v-model="deleteDialog"
      :title="$tc('general.confirm')"
      color="error"
      @confirm="deleteUser(deleteTargetId)"
    >
      <template #activator> </template>

      <v-card-text>
        <v-alert v-if="isUserOwnAccount" type="warning" text outlined>
          {{ $t("general.confirm-delete-own-admin-account") }}
        </v-alert>
        {{ $t("general.confirm-delete-generic") }}
      </v-card-text>
    </BaseDialog>

    <BaseCardSectionTitle :title="$tc('user.user-management')"> </BaseCardSectionTitle>
    <section>
      <v-toolbar color="transparent" flat class="justify-between">
        <BaseButton to="/admin/manage/users/create" class="mr-2">
          {{ $t("general.create") }}
        </BaseButton>
        <BaseButton class="mr-2" color="info" :icon="$globals.icons.link" @click="inviteDialog = true">
          {{ $t("group.invite") }}
        </BaseButton>

        <BaseOverflowButton mode="event" :items="ACTIONS_OPTIONS" @unlock-all-users="unlockAllUsers">
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
              deleteTargetId = item.id;
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
import { defineComponent, reactive, ref, toRefs, useContext, useRouter, computed } from "@nuxtjs/composition-api";
import { useAdminApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { useUser, useAllUsers } from "~/composables/use-user";
import { UserOut } from "~/lib/api/types/user";
import UserInviteDialog from "~/components/Domain/User/UserInviteDialog.vue";

export default defineComponent({
  components: {
    UserInviteDialog,
  },
  layout: "admin",
  setup() {
    const api = useAdminApi();
    const refUserDialog = ref();
    const inviteDialog = ref();
    const { $auth } = useContext();

    const user = computed(() => $auth.user);

    const { $globals, i18n } = useContext();

    const router = useRouter();

    const isUserOwnAccount = computed(() => {
      return state.deleteTargetId === user.value?.id;
    });

    const ACTIONS_OPTIONS = [
      {
        text: i18n.t("user.reset-locked-users"),
        icon: $globals.icons.lock,
        event: "unlock-all-users",
      },
    ];

    const state = reactive({
      deleteDialog: false,
      deleteTargetId: "",
      search: "",
      groups: [],
      households: [],
      sendTo: "",
    });

    const { users, refreshAllUsers } = useAllUsers();
    const { loading, deleteUser: deleteUserMixin } = useUser(refreshAllUsers);

    function deleteUser(id: string) {
      deleteUserMixin(id);

      if (isUserOwnAccount.value) {
        $auth.logout();
      }
    }

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
      { text: i18n.t("household.household"), value: "household" },
      { text: i18n.t("user.auth-method"), value: "authMethod" },
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
      isUserOwnAccount,
      unlockAllUsers,
      ...toRefs(state),
      headers,
      deleteUser,
      loading,
      refUserDialog,
      inviteDialog,
      users,
      user,
      handleRowClick,
      ACTIONS_OPTIONS,
    };
  },
  head() {
    return {
      title: this.$t("sidebar.manage-users") as string,
    };
  },
});
</script>
