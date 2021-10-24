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

    <section>
      <BaseCardSectionTitle :icon="$globals.icons.cog" title="General Configuration"> </BaseCardSectionTitle>
      <v-card class="mb-4">
        <v-list-item>
          <v-list-item-avatar>
            <v-icon :color="getColor(appConfig.baseUrlSet)">
              {{ appConfig.baseUrlSet ? $globals.icons.checkboxMarkedCircle : $globals.icons.close }}
            </v-icon>
          </v-list-item-avatar>
          <v-list-item-content>
            <v-list-item-title :class="getTextClass(appConfig.baseUrlSet)"> Server Side Base URL </v-list-item-title>
            <v-list-item-subtitle :class="getTextClass(appConfig.baseUrlSet)">
              {{ appConfig.baseUrlSet ? "Ready" : "Not Ready - `BASE_URL` still default on API Server" }}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-card>
    </section>
    <section>
      <BaseCardSectionTitle class="pt-2" :icon="$globals.icons.email" title="Email Configuration">
      </BaseCardSectionTitle>
      <v-card>
        <v-card-text>
          <v-list-item>
            <v-list-item-avatar>
              <v-icon :color="getColor(appConfig.emailReady)">
                {{ appConfig.emailReady ? $globals.icons.checkboxMarkedCircle : $globals.icons.close }}
              </v-icon>
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title :class="getTextClass(appConfig.emailReady)">
                Email Configuration Status
              </v-list-item-title>
              <v-list-item-subtitle :class="getTextClass(appConfig.emailReady)">
                {{ appConfig.emailReady ? "Ready" : "Not Ready - Check Env Variables" }}
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
          <v-card-actions>
            <v-text-field v-model="address" class="mr-4" :label="$t('user.email')" :rules="[validators.email]">
            </v-text-field>
            <BaseButton
              color="info"
              :disabled="!appConfig.emailReady || !validEmail"
              :loading="loading"
              @click="testEmail"
            >
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
    </section>
  </v-container>
</template>
    
<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, ref } from "@nuxtjs/composition-api";
import { CheckAppConfig } from "~/api/admin/admin-about";
import { useAdminApi, useApiSingleton } from "~/composables/use-api";
import { validators } from "~/composables/use-validators";

export default defineComponent({
  layout: "admin",
  setup() {
    const state = reactive({
      loading: false,
      address: "",
      success: false,
      error: "",
      tested: false,
    });

    const appConfig = ref<CheckAppConfig>({
      emailReady: false,
      baseUrlSet: false,
    });

    const api = useApiSingleton();

    const adminAPI = useAdminApi();
    onMounted(async () => {
      const { data } = await adminAPI.about.checkApp();

      if (data) {
        appConfig.value = data;
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

    function getTextClass(booly: boolean | any) {
      return booly ? "success--text" : "error--text";
    }
    function getColor(booly: boolean | any) {
      return booly ? "success" : "error";
    }

    return {
      getColor,
      getTextClass,
      appConfig,
      validEmail,
      validators,
      ...toRefs(state),
      testEmail,
    };
  },
  head() {
    return {
      title: this.$t("settings.site-settings") as string,
    };
  },
});
</script>
    
<style scoped>
</style>