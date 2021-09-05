<template>
  <v-container class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="200px" max-width="200px" :src="require('~/static/svgs/manage-api-tokens.svg')"></v-img>
      </template>
      <template #title> API Tokens </template>
      You have {{ user.tokens.length }} active tokens.
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
              :append-outer-icon="$globals.icons.contentCopy"
              @click="copyToken"
              @click:append-outer="copyToken"
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
        <v-expand-transition>
          <v-card-actions v-show="name != ''">
            <v-spacer></v-spacer>
            <BaseButton v-if="createdToken" cancel @click="resetCreate()"> Close </BaseButton>
            <BaseButton v-else :cancel="false" @click="createToken(name)"> Generate </BaseButton>
          </v-card-actions>
        </v-expand-transition>
      </v-card>
    </section>
    <BaseCardSectionTitle class="mt-10" title="Active Tokens"> </BaseCardSectionTitle>
    <section class="d-flex flex-column align-center justify-center">
      <div v-for="(token, index) in $auth.user.tokens" :key="index" class="d-flex my-2">
        <v-card outlined width="500px">
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>
                {{ token.name }}
              </v-list-item-title>
              <v-list-item-subtitle> Created on: {{ $d(token.created_at) }} </v-list-item-subtitle>
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
import { useApiSingleton } from "~/composables/use-api";

export default defineComponent({
  setup() {
    const nuxtContext = useContext();

    const user = computed(() => {
      return nuxtContext.$auth.user;
    });

    const api = useApiSingleton();

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

    async function deleteToken(id: string | number) {
      const { data } = await api.users.deleteAPIToken(id);
      nuxtContext.$auth.fetchUser();
      return data;
    }

    function copyToken() {
      navigator.clipboard.writeText(createdToken.value).then(
        () => console.log("Copied", createdToken.value),
        () => console.log("Copied Failed", createdToken.value)
      );
    }

    return { createToken, deleteToken, copyToken, createdToken, loading, name, user, resetCreate };
  },
});
</script>
    
