<template>
  <v-container class="narrow-container">
    <BasePageTitle class="mb-2">
      <template #header>
        <v-img max-height="125" max-width="125" :src="require('~/static/svgs/manage-profile.svg')"></v-img>
      </template>
      <template #title> Admin User Creation </template>
    </BasePageTitle>
    <AppToolbar back> </AppToolbar>
    <v-form ref="refNewUserForm" @submit.prevent="handleSubmit">
      <v-card outlined>
        <v-card-text>
          <v-select
            v-if="groups"
            v-model="newUserData.group"
            :items="groups"
            rounded
            class="rounded-lg"
            item-text="name"
            item-value="name"
            :return-object="false"
            filled
            label="User Group"
            :rules="[validators.required]"
          ></v-select>
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
import { defineComponent, useRouter, reactive, ref, toRefs } from "@nuxtjs/composition-api";
import { useAdminApi } from "~/composables/api";
import { useGroups } from "~/composables/use-groups";
import { useUserForm } from "~/composables/use-users";
import { validators } from "~/composables/use-validators";

export default defineComponent({
  layout: "admin",
  setup() {
    const { userForm } = useUserForm();
    const { groups } = useGroups();
    const router = useRouter();

    // ==============================================
    // New User Form

    const refNewUserForm = ref<VForm | null>(null);

    const adminApi = useAdminApi();

    const state = reactive({
      newUserData: {
        username: "",
        fullName: "",
        email: "",
        admin: false,
        group: "",
        advanced: false,
        canInvite: false,
        canManage: false,
        canOrganize: false,
        password: "",
      },
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
      validators,
    };
  },
});
</script>

<style lang="scss" scoped>
</style>