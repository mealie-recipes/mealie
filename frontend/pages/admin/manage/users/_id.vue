<template>
  <v-container v-if="user" class="narrow-container">
    <BasePageTitle>
      <template #header>
        <v-img max-height="125" max-width="125" :src="require('~/static/svgs/manage-profile.svg')"></v-img>
      </template>
      <template #title> {{ $t("user.admin-user-management") }} </template>
      {{ $t("user.changes-reflected-immediately") }}
    </BasePageTitle>
    <AppToolbar back> </AppToolbar>
    <v-form v-if="!userError" ref="refNewUserForm" @submit.prevent="handleSubmit">
      <v-card outlined>
        <v-card-text>
          <div class="d-flex">
            <p> {{ $t("user.user-id-with-value", {id: user.id} ) }}</p>
          </div>
          <!-- This is disabled since we can't properly handle changing the user's group in most scenarios -->
          <v-select
            v-if="groups"
            v-model="user.group"
            disabled
            :items="groups"
            rounded
            class="rounded-lg"
            item-text="name"
            item-value="name"
            :return-object="false"
            filled
            :label="$tc('group.user-group')"
            :rules="[validators.required]"
          />
          <v-select
            v-if="households"
            v-model="user.household"
            :items="households"
            rounded
            class="rounded-lg"
            item-text="name"
            item-value="name"
            :return-object="false"
            filled
            :label="$tc('household.user-household')"
            :rules="[validators.required]"
          />
          <div class="d-flex py-2 pr-2">
            <BaseButton type="button" :loading="generatingToken" create @click.prevent="handlePasswordReset">
              {{ $t("user.generate-password-reset-link") }}
            </BaseButton>
          </div>
          <div v-if="resetUrl" class="mb-2">
            <v-card-text>
              <p class="text-center pb-0">
                {{ resetUrl }}
              </p>
            </v-card-text>
            <v-card-actions class="align-center pt-0" style="gap: 4px">
              <BaseButton cancel @click="resetUrl = ''"> {{ $t("general.close") }} </BaseButton>
              <v-spacer></v-spacer>
              <BaseButton v-if="user.email" color="info" class="mr-1" @click="sendResetEmail">
                <template #icon>
                  {{ $globals.icons.email }}
                </template>
                {{ $t("user.email") }}
              </BaseButton>
              <AppButtonCopy :icon="false" color="info" :copy-text="resetUrl" />
            </v-card-actions>
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
import { computed, defineComponent, useRoute, onMounted, ref, useContext } from "@nuxtjs/composition-api";
import { useAdminApi, useUserApi } from "~/composables/api";
import { useGroups } from "~/composables/use-groups";
import { useAdminHouseholds } from "~/composables/use-households";
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
    const { useHouseholdsInGroup } = useAdminHouseholds();
    const { i18n } = useContext();
    const route = useRoute();

    const userId = route.value.params.id;

    // ==============================================
    // New User Form

    const refNewUserForm = ref<VForm | null>(null);

    const adminApi = useAdminApi();

    const user = ref<UserOut | null>(null);
    const households = useHouseholdsInGroup(computed(() => user.value?.groupId || ""));

    const disabledFields = computed(() => {
      return user.value?.authMethod !== "Mealie" ? ["admin"] : [];
    })

    const userError = ref(false);

    const resetUrl = ref<string | null>(null);
    const generatingToken = ref(false);

    onMounted(async () => {
      const { data, error } = await adminApi.users.getOne(userId);

      if (error?.response?.status === 404) {
        alert.error(i18n.tc("user.user-not-found"));
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
        resetUrl.value = `${window.location.origin}/reset-password/?token=${token}`;
      }

      generatingToken.value = false;
    }

    const userApi = useUserApi();
    async function sendResetEmail() {
      if (!user.value?.email) return;
      const { response } = await userApi.email.sendForgotPassword({ email: user.value.email });
      if (response && response.status === 200) {
        alert.success(i18n.tc("profile.email-sent"));
      } else {
        alert.error(i18n.tc("profile.error-sending-email"));
      }
    }

    return {
      user,
      disabledFields,
      userError,
      userForm,
      refNewUserForm,
      handleSubmit,
      groups,
      households,
      validators,
      handlePasswordReset,
      resetUrl,
      generatingToken,
      sendResetEmail,
    };
  },
});
</script>
