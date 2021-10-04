<template>
  <v-container fluid class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img
          max-height="200"
          max-width="150"
          class="mb-2"
          :src="require('~/static/svgs/admin-site-settings.svg')"
        ></v-img>
      </template>
      <template #title> {{ $t("settings.site-settings") }} </template>
    </BasePageTitle>
    <BaseCardSectionTitle :icon="$globals.icons.email" title="Email Configuration"> </BaseCardSectionTitle>
    <v-card>
      <v-card-text>
        <v-list-item>
          <v-list-item-avatar>
            <v-icon :color="ready ? 'success' : 'error'">
              {{ ready ? $globals.icons.check : $globals.icons.close }}
            </v-icon>
          </v-list-item-avatar>
          <v-list-item-content>
            <v-list-item-title
              :class="{
                'success--text': ready,
                'error--text': !ready,
              }"
            >
              Email Configuration Status
            </v-list-item-title>
            <v-list-item-subtitle
              :class="{
                'success--text': ready,
                'error--text': !ready,
              }"
            >
              {{ ready ? "Ready" : "Not Ready - Check Env Variables" }}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <v-card-actions>
          <v-text-field v-model="address" class="mr-4" :label="$t('user.email')" :rules="[validators.email]">
          </v-text-field>
          <BaseButton color="info" :disabled="!ready || !validEmail" :loading="loading" @click="testEmail">
            <template #icon> {{ $globals.icons.email }} </template>
            {{ $t("general.test") }}
          </BaseButton>
        </v-card-actions>
      </v-card-text>
      <template v-if="tested">
        <v-divider class="my-x"></v-divider>
        <v-card-text>
          Email Test Result: {{ success ? "Succeeded" : "Failed" }}
          <div>Errors: {{ error }}</div>
        </v-card-text>
      </template>
    </v-card>
  </v-container>
</template>
    
<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs } from "@nuxtjs/composition-api";
import { useApiSingleton } from "~/composables/use-api";
import { validators } from "~/composables/use-validators";

export default defineComponent({
  layout: "admin",
  setup() {
    const state = reactive({
      ready: true,
      loading: false,
      address: "",
      success: false,
      error: "",
      tested: false,
    });

    const api = useApiSingleton();

    onMounted(async () => {
      const { data } = await api.email.check();

      if (data) {
        state.ready = data.ready;
      }
    });

    async function testEmail() {
      state.loading = true;
      state.tested = false;
      const { data } = await api.email.test({ email: state.address });

      if (data) {
        if (data.success) {
          state.success = true;
        } else {
          state.error = data.error;
          state.success = false;
        }
      }
      state.loading = false;
      state.tested = true;
    }

    const validEmail = computed(() => {
      if (state.address === "") {
        return false;
      }
      const valid = validators.email(state.address);

      // Explicit bool check because validators.email sometimes returns a string
      if (valid === true) {
        return true;
      }
      return false;
    });

    return {
      validEmail,
      validators,
      ...toRefs(state),
      testEmail,
    };
  },
});
</script>
    
<style scoped>
</style>