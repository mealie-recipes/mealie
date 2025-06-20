<template>
  <v-container>
    <BasePageTitle divider>
      <template #header>
        <v-img
          width="100%"
          max-height="125"
          max-width="125"
          :src="require('~/static/svgs/manage-members.svg')"
        />
      </template>
      <template #title>
        {{ $t('group.manage-members') }}
      </template>
      <i18n-t keypath="group.manage-members-description">
        <template #manage>
          <b>{{ $t('group.manage') }}</b>
        </template>
        <template #invite>
          <b>{{ $t('group.invite') }}</b>
        </template>
      </i18n-t>
      <v-container class="mt-1 px-0">
        <nuxt-link
          class="text-center"
          :to="`/user/profile/edit`"
        > {{ $t('group.looking-to-update-your-profile') }}
        </nuxt-link>
      </v-container>
    </BasePageTitle>
    <v-data-table
      :headers="headers"
      :items="members || []"
      item-key="id"
      class="elevation-0"
      hide-default-footer
      disable-pagination
    >
      <template #[`item.avatar`]="{ item }">
        <UserAvatar
          v-if="item"
          :tooltip="false"
          :user-id="item.id"
        />
      </template>
      <template #[`item.admin`]="{ item }">
        {{ item && item.admin ? $t('user.admin') : $t('user.user') }}
      </template>
      <template #[`item.manageHousehold`]="{ item }">
        <div
          v-if="item"
          class="d-flex justify-center"
        >
          <v-checkbox
            v-model="item.canManageHousehold"
            :disabled="item.id === sessionUser?.id || item.admin"
            color="primary"
            class=""
            style="max-width: 30px"
            hide-details
            @change="setPermissions(item)"
          />
        </div>
      </template>
      <template #[`item.manage`]="{ item }">
        <div
          v-if="item"
          class="d-flex justify-center"
        >
          <v-checkbox
            v-model="item.canManage"
            :disabled="item.id === sessionUser?.id || item.admin"
            class=""
            style="max-width: 30px"
            hide-details
            color="primary"
            @change="setPermissions(item)"
          />
        </div>
      </template>
      <template #[`item.organize`]="{ item }">
        <div
          v-if="item"
          class="d-flex justify-center"
        >
          <v-checkbox
            v-model="item.canOrganize"
            :disabled="item.id === sessionUser?.id || item.admin"
            class=""
            style="max-width: 30px"
            hide-details
            color="primary"
            @change="setPermissions(item)"
          />
        </div>
      </template>
      <template #[`item.invite`]="{ item }">
        <div
          v-if="item"
          class="d-flex justify-center"
        >
          <v-checkbox
            v-model="item.canInvite"
            :disabled="item.id === sessionUser?.id || item.admin"
            class=""
            style="max-width: 30px"
            hide-details
            color="primary"
            @change="setPermissions(item)"
          />
        </div>
      </template>
    </v-data-table>
  </v-container>
</template>

<script lang="ts">
import { useUserApi } from "~/composables/api";
import type { UserOut } from "~/lib/api/types/user";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";

export default defineNuxtComponent({
  components: {
    UserAvatar,
  },
  middleware: ["sidebase-auth"],
  setup() {
    const $auth = useMealieAuth();
    const api = useUserApi();
    const i18n = useI18n();

    useSeoMeta({
      title: i18n.t("profile.members"),
    });

    const members = ref<UserOut[] | null[]>([]);

    const headers = [
      { title: "", value: "avatar", sortable: false, align: "center" },
      { title: i18n.t("user.username"), value: "username" },
      { title: i18n.t("user.full-name"), value: "fullName" },
      { title: i18n.t("user.admin"), value: "admin" },
      { title: i18n.t("group.manage"), value: "manage", sortable: false, align: "center" },
      { title: i18n.t("settings.organize"), value: "organize", sortable: false, align: "center" },
      { title: i18n.t("group.invite"), value: "invite", sortable: false, align: "center" },
      { title: i18n.t("group.manage-household"), value: "manageHousehold", sortable: false, align: "center" },
    ];

    async function refreshMembers() {
      const { data } = await api.households.fetchMembers();
      if (data) {
        members.value = data.items;
      }
    }

    async function setPermissions(user: UserOut) {
      const payload = {
        userId: user.id,
        canInvite: user.canInvite,
        canManageHousehold: user.canManageHousehold,
        canManage: user.canManage,
        canOrganize: user.canOrganize,
      };

      await api.households.setMemberPermissions(payload);
    }

    onMounted(async () => {
      await refreshMembers();
    });

    return { members, headers, setPermissions, sessionUser: $auth.user };
  },
});
</script>
