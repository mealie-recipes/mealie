<template>
  <v-container class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="200px" max-width="200px" :src="require('~/static/svgs/manage-api-tokens.svg')"></v-img>
      </template>
      <template #title> {{ $tc("settings.token.api-tokens") }} </template>
      {{ $tc('settings.token.you-have-token-count', user.tokens.length) }}
    </BasePageTitle>
    <section class="d-flex justify-center">
      <v-card class="mt-4" width="500px">
        <v-card-text>
          <v-form ref="domNewTokenForm" @submit.prevent>
            <v-text-field v-model="name" :label="$t('settings.token.token-name')"> </v-text-field>
          </v-form>

          <template v-if="createdToken != ''">
            <v-textarea
              v-model="createdToken"
              class="mb-0 pb-0"
              :label="$t('settings.token.api-token')"
              readonly
              rows="3"
            >
            </v-textarea>
            <v-subheader class="text-center">
              {{
                $t(
                  "settings.token.copy-this-token-for-use-with-an-external-application-this-token-will-not-be-viewable-again"
                )
              }}
            </v-subheader>
          </template>
        </v-card-text>
        <v-card-actions>
          <BaseButton v-if="createdToken" cancel @click="resetCreate()"> {{ $t('general.close') }} </BaseButton>
          <v-spacer></v-spacer>
          <AppButtonCopy v-if="createdToken" :icon="false" color="info" :copy-text="createdToken"> </AppButtonCopy>
          <BaseButton v-else key="generate-button" :disabled="name == ''" @click="createToken(name)">
            {{ $t('settings.token.generate') }}
          </BaseButton>
        </v-card-actions>
      </v-card>
    </section>
    <BaseCardSectionTitle class="mt-10" :title="$tc('settings.token.active-tokens')"> </BaseCardSectionTitle>
    <section class="d-flex flex-column">
      <div v-for="(token, index) in $auth.user.tokens" :key="index">
        <v-card outlined class="mb-2">
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>
                {{ token.name }}
              </v-list-item-title>
              <v-list-item-subtitle> {{ $t('general.created-on-date', [$d(new Date(token.createdAt))]) }} </v-list-item-subtitle>
            </v-list-item-content>
            <v-list-item-action>
              <BaseButton delete small @click="deleteToken(token.id)"></BaseButton>
            </v-list-item-action>
          </v-list-item>
        </v-card>
      </div>
    </section>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, useContext, ref } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { VForm } from "~/types/vuetify";

export default defineComponent({
  middleware: ["auth", "advanced-only"],
  setup() {
    const nuxtContext = useContext();

    const user = computed(() => {
      return nuxtContext.$auth.user;
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
      nuxtContext.$auth.fetchUser();
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
      nuxtContext.$auth.fetchUser();
      return data;
    }

    return { createToken, deleteToken, createdToken, loading, name, user, resetCreate };
  },
  head() {
    return {
      title: this.$t("settings.token.api-tokens") as string,
    };
  },
});
</script>
