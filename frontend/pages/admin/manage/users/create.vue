<template>
  <v-container class="narrow-container">
    <BasePageTitle class="mb-2">
      <template #header>
        <v-img max-height="125" max-width="125" :src="require('~/static/svgs/manage-profile.svg')"></v-img>
      </template>
      <template #title> {{ $t('user.admin-user-creation') }} </template>
    </BasePageTitle>
    <AppToolbar back> </AppToolbar>
    <v-form ref="refNewUserForm" @submit.prevent="handleSubmit">
      <v-card outlined>
        <v-card-text>
          <v-select
            v-model="selectedGroupId"
            :items="groups"
            rounded
            class="rounded-lg"
            item-text="name"
            item-value="id"
            :return-object="false"
            filled
            :label="$t('group.user-group')"
            :rules="[validators.required]"
          />
          <v-select
            v-model="newUserData.household"
            :disabled="!selectedGroupId"
            :items="households"
            rounded
            class="rounded-lg"
            item-text="name"
            item-value="name"
            :return-object="false"
            filled
            :label="$t('household.user-household')"
            :hint="selectedGroupId ? '' : $tc('group.you-must-select-a-group-before-selecting-a-household')"
            persistent-hint
            :rules="[validators.required]"
          />
          <AutoForm v-model="newUserData" :items="userForm" />
        </v-card-text>
      </v-card>
      <div class="d-flex pa-2">
        <BaseButton type="submit" class="ml-auto"></BaseButton>
      </div>
    </v-form>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, useRouter, reactive, ref, toRefs, watch } from "@nuxtjs/composition-api";
import { useAdminApi } from "~/composables/api";
import { useGroups } from "~/composables/use-groups";
import { useAdminHouseholds } from "~/composables/use-households";
import { useUserForm } from "~/composables/use-users";
import { validators } from "~/composables/use-validators";
import { VForm } from "~/types/vuetify";

export default defineComponent({
  layout: "admin",
  setup() {
    const { userForm } = useUserForm();
    const { groups } = useGroups();
    const { useHouseholdsInGroup } = useAdminHouseholds();
    const router = useRouter();

    // ==============================================
    // New User Form

    const refNewUserForm = ref<VForm | null>(null);

    const adminApi = useAdminApi();

    const selectedGroupId = ref<string>("");
    const households = useHouseholdsInGroup(selectedGroupId);

    const selectedGroup = computed(() => {
      return groups.value?.find((group) => group.id === selectedGroupId.value);
    });
    const state = reactive({
      newUserData: {
        username: "",
        fullName: "",
        email: "",
        admin: false,
        group: selectedGroup.value?.name || "",
        household: "",
        advanced: false,
        canInvite: false,
        canManage: false,
        canOrganize: false,
        password: "",
        authMethod: "Mealie",
      },
    });
    watch(selectedGroup, (newGroup) => {
      state.newUserData.group = newGroup?.name || "";
      state.newUserData.household = "";
    });

    async function handleSubmit() {
      if (!refNewUserForm.value?.validate()) return;

      const { response } = await adminApi.users.createOne(state.newUserData);

      if (response?.status === 201) {
        router.push("/admin/manage/users");
      }
    }

    return {
      ...toRefs(state),
      userForm,
      refNewUserForm,
      handleSubmit,
      groups,
      selectedGroupId,
      households,
      validators,
    };
  },
});
</script>

<style lang="scss" scoped></style>
