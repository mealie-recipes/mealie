<template>
  <v-container class="narrow-container">
    <BasePageTitle class="mb-2">
      <template #header>
        <v-img
          width="100%"
          max-height="125"
          max-width="125"
          src="/svgs/manage-profile.svg"
        />
      </template>
      <template #title>
        {{ $t('user.admin-user-creation') }}
      </template>
    </BasePageTitle>
    <AppToolbar back />
    <v-form
      ref="refNewUserForm"
      @submit.prevent="handleSubmit"
    >
      <v-card variant="outlined">
        <v-card-text>
          <v-sheet>
            <v-row>
              <v-col cols="6">
                <v-select
                  v-model="selectedGroup"
                  :items="groups || []"
                  item-title="name"
                  return-object
                  variant="filled"
                  :label="$t('group.user-group')"
                  :rules="[validators.required]"
                />
              </v-col>
              <v-col cols="6">
                <v-select
                  v-model="newUserData.household"
                  :disabled="!selectedGroup"
                  :items="households"
                  item-title="name"
                  item-value="name"
                  variant="filled"
                  :label="$t('household.user-household')"
                  :hint="selectedGroup ? '' : $t('group.you-must-select-a-group-before-selecting-a-household')"
                  persistent-hint
                  :rules="[validators.required]"
                />
              </v-col>
            </v-row>
          </v-sheet>
          <AutoForm
            v-model="newUserData"
            :items="userForm"
            :disabled-fields="disabledFields"
          />
        </v-card-text>
      </v-card>
      <div class="d-flex pa-2">
        <BaseButton
          type="submit"
          class="ml-auto"
        />
      </div>
    </v-form>
  </v-container>
</template>

<script setup lang="ts">
import { useAdminApi } from "~/composables/api";
import { useGroups } from "~/composables/use-groups";
import { useUserForm } from "~/composables/use-users";
import { validators } from "~/composables/use-validators";
import type { GroupInDB, UserIn } from "~/lib/api/types/user";
import type { VForm } from "~/types/auto-forms";

definePageMeta({
  layout: "admin",
});
const { userForm } = useUserForm();
const { groups } = useGroups();
const router = useRouter();

const refNewUserForm = ref<VForm | null>(null);
const adminApi = useAdminApi();

const selectedGroup = ref<GroupInDB | undefined>(undefined);
const households = computed(() => selectedGroup.value?.households || []);

const newUserData = ref({
  username: "",
  fullName: "",
  email: "",
  admin: false,
  group: computed(() => selectedGroup.value?.name || ""),
  household: "",
  advanced: false,
  canInvite: false,
  canManage: false,
  canOrganize: false,
  password: "",
  authMethod: "Mealie",
});

const disabledFields = computed(() => {
  const fields: string[] = [];
  if (newUserData.value.admin) {
    fields.push("canManageHousehold", "canManage", "advanced");
  }
  if (newUserData.value.admin || !newUserData.value.canManage) {
    fields.push("canOrganize", "canInvite");
  }
  return fields;
});

watch(
  () => newUserData.value.admin,
  (isAdmin, wasAdmin) => {
    if (isAdmin && !wasAdmin) {
      newUserData.value.canManageHousehold = true;
      newUserData.value.canManage = true;
      newUserData.value.canOrganize = true;
      newUserData.value.canInvite = true;
      newUserData.value.advanced = true;
    }
    else if (!isAdmin && wasAdmin) {
      newUserData.value.canManageHousehold = false;
      newUserData.value.canManage = false;
      newUserData.value.canOrganize = false;
      newUserData.value.canInvite = false;
      newUserData.value.advanced = false;
    }
  },
);

watch(
  () => newUserData.value.canManage,
  (canManage, wasCanManage) => {
    if (newUserData.value.admin) {
      return;
    }
    if (!canManage && wasCanManage) {
      newUserData.value.canOrganize = false;
      newUserData.value.canInvite = false;
    }
  },
);

async function handleSubmit() {
  if (!refNewUserForm.value?.validate()) return;

  const { response } = await adminApi.users.createOne(newUserData.value as UserIn);

  if (response?.status === 201) {
    router.push("/admin/manage/users");
  }
}
</script>

<style lang="scss" scoped></style>
