<template>
  <BaseStatCard :icon="$globals.icons.api" color="accent">
    <template #after-heading>
      <div class="ml-auto text-right">
        <h2 class="body-3 grey--text font-weight-light">
          {{ $t("settings.token.api-tokens") }}
        </h2>
        <h3 class="display-2 font-weight-light text--primary">
          <small> {{ tokens.length }} </small>
        </h3>
      </div>
    </template>
    <template #bottom>
      <v-subheader class="mb-n2">{{ $t("settings.token.active-tokens") }}</v-subheader>
      <v-virtual-scroll height="210" item-height="70" :items="tokens" class="mt-2">
        <template #default="{ item }">
          <v-divider></v-divider>
          <v-list-item @click.prevent>
            <v-list-item-avatar>
              <v-icon large dark color="accent">
                {{ $globals.icons.api }}
              </v-icon>
            </v-list-item-avatar>

            <v-list-item-content>
              <v-list-item-title v-text="item.name"></v-list-item-title>
            </v-list-item-content>

            <v-list-item-action class="ml-auto">
              <v-btn large icon @click.stop="deleteToken(item.id)">
                <v-icon color="accent">{{ $globals.icons.delete }}</v-icon>
              </v-btn>
            </v-list-item-action>
          </v-list-item>
          <v-divider></v-divider>
        </template>
      </v-virtual-scroll>

      <v-divider></v-divider>
      <v-card-actions class="pb-1 pt-3">
        <v-spacer></v-spacer>
        <BaseDialog
          :title="$t('settings.token.create-an-api-token')"
          :title-icon="$globals.icons.api"
          :submit-text="buttonText"
          :loading="loading"
          @submit="createToken(name)"
        >
          <v-card-text>
            <v-form ref="domNewTokenForm" @submit.prevent>
              <v-text-field v-model="name" :label="$t('settings.token.token-name')" required> </v-text-field>
            </v-form>

            <div v-if="createdToken != ''">
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
            </div>
          </v-card-text>

          <template #activator="{ open }">
            <BaseButton create @click="open" />
          </template>
        </BaseDialog>
      </v-card-actions>
    </template>
  </BaseStatCard>
</template>

<script lang="ts">
import { defineComponent, ref } from "@nuxtjs/composition-api";
import { useApiSingleton } from "~/composables/use-api";

const REFRESH_EVENT = "refresh";

export default defineComponent({
  props: {
    tokens: {
      type: Array,
      default: () => [],
    },
  },
  setup(_, context) {
    const api = useApiSingleton();

    const domNewTokenForm = ref<VForm | null>(null);

    const createdToken = ref("");
    const name = ref("");
    const loading = ref(false);

    function resetCreate() {
      createdToken.value = "";
      loading.value = false;
      name.value = "";
      context.emit(REFRESH_EVENT);
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
      context.emit(REFRESH_EVENT);
      return data;
    }

    function copyToken() {
      navigator.clipboard.writeText(createdToken.value).then(
        () => console.log("Copied", createdToken.value),
        () => console.log("Copied Failed", createdToken.value)
      );
    }

    return { createToken, deleteToken, copyToken, createdToken, loading, name };
  },
  computed: {
    buttonText(): any {
      if (this.createdToken === "") {
        return this.$t("general.create");
      } else {
        return this.$t("general.close");
      }
    },
  },
});
</script>

