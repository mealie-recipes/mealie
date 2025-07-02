<template>
  <v-container
    v-if="group"
    class="narrow-container"
  >
    <BasePageTitle>
      <template #header>
        <v-img
          width="100%"
          max-height="125"
          max-width="125"
          :src="require('~/static/svgs/manage-group-settings.svg')"
        />
      </template>
      <template #title>
        {{ $t('group.admin-group-management') }}
      </template>
      {{ $t('group.admin-group-management-text') }}
    </BasePageTitle>
    <AppToolbar back />
    <v-card-text> {{ $t('group.group-id-value', [group.id]) }} </v-card-text>
    <v-form
      v-if="!userError"
      ref="refGroupEditForm"
      @submit.prevent="handleSubmit"
    >
      <v-card variant="outlined" style="border-color: lightgrey;">
        <v-card-text>
          <v-text-field
            v-model="group.name"
            :label="$t('group.group-name')"
          />
          <GroupPreferencesEditor
            v-if="group.preferences"
            v-model="group.preferences"
          />
        </v-card-text>
      </v-card>
      <div class="d-flex pa-2">
        <BaseButton
          type="submit"
          edit
          class="ml-auto"
        >
          {{ $t("general.update") }}
        </BaseButton>
      </div>
    </v-form>
  </v-container>
</template>

<script lang="ts">
import GroupPreferencesEditor from "~/components/Domain/Group/GroupPreferencesEditor.vue";
import { useAdminApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";

export default defineNuxtComponent({
  components: {
    GroupPreferencesEditor,
  },
  setup() {
    definePageMeta({
      layout: "admin",
    });

    const route = useRoute();

    const i18n = useI18n();

    const groupId = computed(() => route.params.id as string);

    // ==============================================
    // New User Form

    const refGroupEditForm = ref<VForm | null>(null);

    const adminApi = useAdminApi();

    const userError = ref(false);

    const { data: group } = useLazyAsyncData(`get-household-${groupId.value}`, async () => {
      if (!groupId.value) {
        return null;
      }
      const { data, error } = await adminApi.groups.getOne(groupId.value);

      if (error?.response?.status === 404) {
        alert.error(i18n.t("user.user-not-found"));
        userError.value = true;
      }
      return data;
    }, { watch: [groupId] });

    async function handleSubmit() {
      if (!refGroupEditForm.value?.validate() || group.value === null) {
        return;
      }

      const { response, data } = await adminApi.groups.updateOne(group.value.id, group.value);
      if (response?.status === 200 && data) {
        if (group.value.slug !== data.slug) {
          // the slug updated, which invalidates the nav URLs
          window.location.reload();
        }
        group.value = data;
      }
      else {
        alert.error(i18n.t("settings.settings-update-failed"));
      }
    }

    return {
      group,
      userError,
      refGroupEditForm,
      handleSubmit,
    };
  },
});
</script>
