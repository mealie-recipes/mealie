<template>
  <v-container class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img
          width="100%"
          max-height="200px"
          max-width="200px"
          src="/svgs/manage-api-tokens.svg"
        />
      </template>
      <template #title>
        {{ $t("settings.token.api-tokens") }}
      </template>
      {{ $t('settings.token.you-have-token-count', user.tokens!.length) }}
    </BasePageTitle>
    <section class="d-flex justify-center">
      <v-card
        class="mt-4"
        width="100%"
        flat
      >
        <v-card-text class="px-0">
          <v-form
            ref="domNewTokenForm"
            @submit.prevent
          >
            <v-text-field
              v-model="name"
              :label="$t('settings.token.token-name')"
            />
          </v-form>

          <template v-if="createdToken != ''">
            <v-textarea
              v-model="createdToken"
              class="mb-0 pb-0"
              :label="$t('settings.token.api-token')"
              readonly
              rows="3"
            />
            <p>
              {{
                $t(
                  "settings.token.copy-this-token-for-use-with-an-external-application-this-token-will-not-be-viewable-again",
                )
              }}
            </p>
          </template>
        </v-card-text>
        <v-card-actions class="px-0">
          <BaseButton
            v-if="createdToken"
            cancel
            @click="resetCreate()"
          >
            {{ $t('general.close') }}
          </BaseButton>
          <v-spacer />
          <AppButtonCopy
            v-if="createdToken"
            :icon="false"
            color="info"
            :copy-text="createdToken"
          />
          <BaseButton
            v-else
            key="generate-button"
            :disabled="name == ''"
            @click="createToken(name)"
          >
            {{ $t('settings.token.generate') }}
          </BaseButton>
        </v-card-actions>
      </v-card>
    </section>
    <BaseCardSectionTitle
      class="mt-10"
      :title="$t('settings.token.active-tokens')"
    />
    <section class="d-flex flex-column">
      <v-list>
        <div
          v-for="(token, index) in user.tokens"
          :key="index"
        >
          <v-list-item>
            <v-list-item-title>
              {{ token.name }}
            </v-list-item-title>
            <v-list-item-subtitle>
              {{ $t('general.created-on-date', [$d(new Date(token.createdAt!))]) }}
            </v-list-item-subtitle>
            <template #append>
              <BaseButton
                delete
                small
                @click="deleteToken(token.id)"
              />
            </template>
          </v-list-item>
          <v-divider class="mx-2 my-2" />
        </div>
      </v-list>
    </section>
  </v-container>
</template>

<script lang="ts">
import { useUserApi } from "~/composables/api";
import type { VForm } from "~/types/auto-forms";

export default defineNuxtComponent({
  middleware: ["sidebase-auth", "advanced-only"],
  setup() {
    const i18n = useI18n();
    const $auth = useMealieAuth();

    useSeoMeta({
      title: i18n.t("settings.token.api-tokens"),
    });

    const user = computed(() => {
      return $auth.user.value;
    });

    const api = useUserApi();

    const domNewTokenForm = ref<VForm | null>(null);

    const createdToken = ref("");
    const name = ref("");
    const loading = ref(false);

    function resetCreate() {
      createdToken.value = "";
      loading.value = false;
      name.value = "";
      $auth.refresh();
    }

    async function createToken(name: string) {
      if (loading.value) {
        resetCreate();
        return;
      }

      loading.value = true;

      if (domNewTokenForm?.value?.validate()) {
        console.log("Created");
        return;
      }

      const { data } = await api.users.createAPIToken({ name });

      if (data) {
        createdToken.value = data.token;
      }
    }

    async function deleteToken(id: number) {
      const { data } = await api.users.deleteAPIToken(id);
      $auth.refresh();
      return data;
    }

    return { createToken, deleteToken, createdToken, loading, name, user, resetCreate };
  },
});
</script>
