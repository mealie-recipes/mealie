<template>
  <v-container v-if="user" class="narrow-container">
    <BasePageTitle>
      <template #header>
        <v-img max-height="125" max-width="125" :src="require('~/static/svgs/manage-profile.svg')"></v-img>
      </template>
      <template #title> Admin User Management </template>
      Changes to this user will be reflected immediately.
    </BasePageTitle>
    <AppToolbar back> </AppToolbar>
    <v-form v-if="!userError" ref="refNewUserForm" @submit.prevent="handleSubmit">
      <v-card outlined>
        <v-card-text>
          <div class="d-flex">
            <p>User Id: {{ user.id }}</p>
          </div>
          <v-select
            v-if="groups"
            v-model="user.group"
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
          <div class="d-flex py-2 pr-2">
            <BaseButton type="button" :loading="generatingToken" create @click.prevent="handlePasswordReset">
              {{ $t("user.generate-password-reset-link") }}
            </BaseButton>
            <AppButtonCopy v-if="resetUrl" :copy-text="resetUrl"></AppButtonCopy>
          </div>

          <AutoForm v-model="user" :items="userForm" update-mode :disabled-fields="disabledFields" />
        </v-card-text>
      </v-card>
      <div class="d-flex pa-2">
        <BaseButton type="submit" edit class="ml-auto"> {{ $t("general.update") }}</BaseButton>
      </div>
    </v-form>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, useRoute, onMounted, ref } from "@nuxtjs/composition-api";
import { useAdminApi } from "~/composables/api";
import { useGroups } from "~/composables/use-groups";
import { alert } from "~/composables/use-toast";
import { useUserForm } from "~/composables/use-users";
import { validators } from "~/composables/use-validators";
import { VForm } from "~/types/vuetify";
import { UserOut } from "~/lib/api/types/user";

export default defineComponent({
  layout: "admin",
  setup() {
    const { userForm } = useUserForm();
    const { groups } = useGroups();
    const route = useRoute();

    const userId = route.value.params.id;

    // ==============================================
    // New User Form

    const refNewUserForm = ref<VForm | null>(null);

    const adminApi = useAdminApi();

    const user = ref<UserOut | null>(null);
    const disabledFields = computed(() => {
      return user.value?.authMethod === "LDAP" ? ["admin"] : [];
    })

    const userError = ref(false);

    const resetUrl = ref<string | null>(null);
    const generatingToken = ref(false);

    onMounted(async () => {
      const { data, error } = await adminApi.users.getOne(userId);

      if (error?.response?.status === 404) {
        alert.error("User Not Found");
        userError.value = true;
      }

      if (data) {
        user.value = data;
      }
    });

    async function handleSubmit() {
      if (!refNewUserForm.value?.validate() || user.value === null) return;

      const { response, data } = await adminApi.users.updateOne(user.value.id, user.value);

      if (response?.status === 200 && data) {
        user.value = data;
      }
    }

    async function handlePasswordReset() {
      if (user.value === null) return;
      generatingToken.value = true;

      const { response, data } = await adminApi.users.generatePasswordResetToken({ email: user.value.email });

      if (response?.status === 201 && data) {
        const token: string = data.token;
        resetUrl.value = `${window.location.origin}/reset-password?token=${token}`;
      }

      generatingToken.value = false;
    }

    return {
      user,
      disabledFields,
      userError,
      userForm,
      refNewUserForm,
      handleSubmit,
      groups,
      validators,
      handlePasswordReset,
      resetUrl,
      generatingToken,
    };
  },
});
</script>
