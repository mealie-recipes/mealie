<template>
  <v-container>
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="125" max-width="125" :src="require('~/static/svgs/manage-members.svg')"></v-img>
      </template>
      <template #title> {{ $t('group.manage-members') }} </template>
        <i18n path="group.manage-members-description">
          <template #manage>
            <b>{{ $t('group.manage') }}</b>
          </template>
          <template #invite>
            <b>{{ $t('group.invite') }}</b>
          </template>
        </i18n>
        <v-container class="mt-1 px-0">
        <nuxt-link class="text-center" :to="`/user/profile/edit`"> {{ $t('group.looking-to-update-your-profile') }} </nuxt-link>
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
      <template #item.avatar="{ item }">
        <UserAvatar :tooltip="false" :user-id="item.id" />
      </template>
      <template #item.admin="{ item }">
        {{ item.admin ? $t('user.admin') : $t('user.user') }}
      </template>
      <template #item.manageHousehold="{ item }">
        <div class="d-flex justify-center">
          <v-checkbox
            v-model="item.canManageHousehold"
            :disabled="item.id === $auth.user.id || item.admin"
            class=""
            style="max-width: 30px"
            @change="setPermissions(item)"
          ></v-checkbox>
        </div>
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
import { UserOut } from "~/lib/api/types/user";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";

export default defineComponent({
  components: {
    UserAvatar,
  },
  middleware: ["auth"],
  setup() {
    const api = useUserApi();

    const { i18n } = useContext();

    const members = ref<UserOut[] | null[]>([]);

    const headers = [
      { text: "", value: "avatar", sortable: false, align: "center" },
      { text: i18n.t("user.username"), value: "username" },
      { text: i18n.t("user.full-name"), value: "fullName" },
      { text: i18n.t("user.admin"), value: "admin" },
      { text: i18n.t("group.manage"), value: "manage", sortable: false, align: "center" },
      { text: i18n.t("settings.organize"), value: "organize", sortable: false, align: "center" },
      { text: i18n.t("group.invite"), value: "invite", sortable: false, align: "center" },
      { text: i18n.t("group.manage-household"), value: "manageHousehold", sortable: false, align: "center" },
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

    return { members, headers, setPermissions };
  },
  head() {
    return {
      title: this.$t("profile.members"),
    };
  },
});
</script>
