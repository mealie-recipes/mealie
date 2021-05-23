<template>
  <StatCard icon="mdi-api" color="accent">
    <template v-slot:after-heading>
      <div class="ml-auto text-right">
        <h2 class="body-3 grey--text font-weight-light">
          {{ $t("settings.token.api-tokens") }}
        </h2>
        <h3 class="display-2 font-weight-light text--primary">
          <small> {{ user.tokens.length }} </small>
        </h3>
      </div>
    </template>
    <template v-slot:bottom>
      <v-subheader class="mb-n2">{{ $t("settings.token.active-tokens") }}</v-subheader>
      <v-virtual-scroll height="210" item-height="70" :items="user.tokens" class="mt-2">
        <template v-slot:default="{ item }">
          <v-divider></v-divider>
          <v-list-item @click.prevent>
            <v-list-item-avatar>
              <v-icon large dark color="accent">
                mdi-api
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
          title-icon="mdi-api"
          @submit="createToken"
          :submit-text="buttonText"
          :loading="loading"
        >
          <v-card-text>
            <v-form ref="newTokenForm">
              <v-text-field v-model="name" :label="$t('settings.token.token-name')" required> </v-text-field>
            </v-form>

            <div v-if="createdToken != ''">
              <v-textarea
                class="mb-0 pb-0"
                :label="$t('settings.token.api-token')"
                readonly
                v-model="createdToken"
                append-outer-icon="mdi-content-copy"
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

          <template v-slot:open="{ open }">
            <v-btn color="success" @click="open">
              <v-icon left> {{ $globals.icons.create }} </v-icon>
              {{ $t("general.create") }}
            </v-btn>
          </template>
        </BaseDialog>
      </v-card-actions>
    </template>
  </StatCard>
</template>

<script>
import BaseDialog from "@/components/UI/Dialogs/BaseDialog";
import StatCard from "@/components/UI/StatCard";
import { api } from "@/api";
import { validators } from "@/mixins/validators";
import { initials } from "@/mixins/initials";
export default {
  components: {
    BaseDialog,
    StatCard,
  },
  mixins: [validators, initials],
  data() {
    return {
      name: "",
      loading: false,
      createdToken: "",
    };
  },

  mounted() {
    this.$store.dispatch("requestUserData");
  },

  computed: {
    user() {
      return this.$store.getters.getUserData;
    },
    buttonText() {
      if (this.createdToken === "") {
        return this.$t("general.create");
      } else {
        return this.$t("general.close");
      }
    },
  },

  methods: {
    async createToken() {
      if (this.loading === true) {
        this.loading = false;
        this.$store.dispatch("requestUserData");
        this.createdToken = "";
        this.name = "";
        return;
      }
      this.loading = true;
      if (this.$refs.newTokenForm.validate()) {
        const response = await api.users.createAPIToken(this.name);
        this.createdToken = response.token;
      }
    },
    async deleteToken(id) {
      await api.users.deleteAPIToken(id);
      this.$store.dispatch("requestUserData");
    },
    copyToken() {
      const copyText = this.createdToken;
      navigator.clipboard.writeText(copyText).then(
        () => console.log("Copied", copyText),
        () => console.log("Copied Failed", copyText)
      );
    },
  },
};
</script>

<style></style>
