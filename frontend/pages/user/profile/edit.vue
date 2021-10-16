<template>
  <v-container class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="200" max-width="200" class="mb-2" :src="require('~/static/svgs/manage-profile.svg')"></v-img>
      </template>
      <template #title> Your Profile Settings </template>
    </BasePageTitle>

    <section>
      <ToggleState tag="article">
        <template #activator="{ toggle, state }">
          <v-btn v-if="!state" color="info" class="mt-2 mb-n3" @click="toggle">
            <v-icon left>{{ $globals.icons.lock }}</v-icon>
            {{ $t("settings.change-password") }}
          </v-btn>
          <v-btn v-else color="info" class="mt-2 mb-n3" @click="toggle">
            <v-icon left>{{ $globals.icons.user }}</v-icon>
            {{ $t("settings.profile") }}
          </v-btn>
        </template>
        <template #default="{ state }">
          <v-slide-x-transition>
            <div v-if="!state" key="personal-info">
              <BaseCardSectionTitle class="mt-10" title="Personal Information"> </BaseCardSectionTitle>
              <v-card tag="article" outlined>
                <v-card-text class="pb-0">
                  <v-form ref="userUpdate">
                    <v-text-field v-model="userCopy.username" :label="$t('user.username')" required validate-on-blur>
                    </v-text-field>
                    <v-text-field v-model="userCopy.fullName" :label="$t('user.full-name')" required validate-on-blur>
                    </v-text-field>
                    <v-text-field v-model="userCopy.email" :label="$t('user.email')" validate-on-blur required>
                    </v-text-field>
                  </v-form>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <BaseButton update @click="updateUser" />
                </v-card-actions>
              </v-card>
            </div>
            <div v-if="state" key="change-password">
              <BaseCardSectionTitle class="mt-10" :title="$t('settings.change-password')"> </BaseCardSectionTitle>
              <v-card outlined>
                <v-card-text class="pb-0">
                  <v-form ref="passChange">
                    <v-text-field
                      v-model="password.current"
                      :prepend-icon="$globals.icons.lock"
                      :label="$t('user.current-password')"
                      validate-on-blur
                      :type="showPassword ? 'text' : 'password'"
                      @click:append="showPassword.current = !showPassword.current"
                    ></v-text-field>
                    <v-text-field
                      v-model="password.newOne"
                      :prepend-icon="$globals.icons.lock"
                      :label="$t('user.new-password')"
                      :type="showPassword ? 'text' : 'password'"
                      @click:append="showPassword.newOne = !showPassword.newOne"
                    ></v-text-field>
                    <v-text-field
                      v-model="password.newTwo"
                      :prepend-icon="$globals.icons.lock"
                      :label="$t('user.confirm-password')"
                      :rules="[password.newOne === password.newTwo || $t('user.password-must-match')]"
                      validate-on-blur
                      :type="showPassword ? 'text' : 'password'"
                      @click:append="showPassword.newTwo = !showPassword.newTwo"
                    ></v-text-field>
                  </v-form>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <BaseButton update @click="updateUser" />
                </v-card-actions>
              </v-card>
            </div>
          </v-slide-x-transition>
        </template>
      </ToggleState>
    </section>
    <section>
      <BaseCardSectionTitle class="mt-10" title="Preferences"> </BaseCardSectionTitle>
      <v-checkbox
        v-model="userCopy.advanced"
        class="mt-n4"
        label="Show advanced features (API Keys, Webhooks, and Data Management)"
        @change="updateUser"
      ></v-checkbox>
      <div class="d-flex flex-wrap justify-center mt-5">
        <v-btn outlined class="rounded-xl my-1 mx-1" to="/user/profile" nuxt exact>
          <v-icon left>
            {{ $globals.icons.backArrow }}
          </v-icon>
          Back to Profile
        </v-btn>
        <v-btn outlined class="rounded-xl my-1 mx-1" to="/user/group"> Looking for Privacy Settings? </v-btn>
      </div>
    </section>
  </v-container>
</template>
    
<script lang="ts">
import { ref, reactive, defineComponent, computed, useContext, watch } from "@nuxtjs/composition-api";
import { useApiSingleton } from "~/composables/use-api";

export default defineComponent({
  setup() {
    const nuxtContext = useContext();
    const user = computed(() => nuxtContext.$auth.user);

    watch(user, () => {
      userCopy.value = { ...user.value };
    });

    const userCopy = ref({ ...user.value });

    const api = useApiSingleton();

    const domUpdatePassword = ref<VForm | null>(null);
    const password = reactive({
      current: "",
      newOne: "",
      newTwo: "",
    });

    async function updateUser() {
      // @ts-ignore
      const { response } = await api.users.updateOne(userCopy.value.id, userCopy.value);
      if (response?.status === 200) {
        nuxtContext.$auth.fetchUser();
      }
    }

    async function updatePassword() {
      if (!userCopy.value?.id) {
        return;
      }
      // @ts-ignore
      const { response } = await api.users.changePassword(userCopy.value.id, {
        currentPassword: password.current,
        newPassword: password.newOne,
      });

      if (response?.status === 200) {
        console.log("Password Changed");
      }
    }

    return { updateUser, updatePassword, userCopy, password, domUpdatePassword };
  },
  data() {
    return {
      hideImage: false,
      passwordLoading: false,
      showPassword: false,
      loading: false,
    };
  },
  head() {
    return {
      title: this.$t("settings.profile") as string,
    };
  },

  methods: {
    async changePassword() {
      // @ts-ignore
      this.paswordLoading = true;
      const data = {
        currentPassword: this.password.current,
        newPassword: this.password.newOne,
      };

      // @ts-ignore
      if (this.$refs.passChange.validate()) {
        // @ts-ignore
        if (await api.users.changePassword(this.user.id, data)) {
          this.$emit("refresh");
        }
      }

      // @ts-ignore
      this.paswordLoading = false;
    },
  },
});
</script>
    
