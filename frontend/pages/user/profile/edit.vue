<template>
  <v-container class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <div class="d-flex flex-column align-center justify-center">
          <UserAvatar :tooltip="false" size="96" :user-id="$auth.user.id" />
          <AppButtonUpload
            class="my-1"
            file-name="profile"
            accept="image/*"
            :url="`/api/users/${$auth.user.id}/image`"
            @uploaded="$auth.fetchUser()"
          />
        </div>
      </template>
      <template #title> {{ $t("profile.user-settings") }} </template>
    </BasePageTitle>

    <section class="mt-5">
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
          <v-slide-x-transition leave-absolute hide-on-leave>
            <div v-if="!state" key="personal-info">
              <BaseCardSectionTitle class="mt-10" :title="$tc('profile.personal-information')"> </BaseCardSectionTitle>
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
            <div v-else key="change-password">
              <BaseCardSectionTitle class="mt-10" :title="$tc('settings.change-password')"> </BaseCardSectionTitle>
              <v-card outlined>
                <v-card-text class="pb-0">
                  <v-form ref="passChange">
                    <v-text-field
                      v-model="password.current"
                      :prepend-icon="$globals.icons.lock"
                      :label="$t('user.current-password')"
                      validate-on-blur
                      :type="showPassword ? 'text' : 'password'"
                      :append-icon="showPassword ? $globals.icons.eye : $globals.icons.eyeOff"
                      :rules="[validators.minLength(1)]"
                      @click:append="showPassword = !showPassword"
                    />
                    <v-text-field
                      v-model="password.newOne"
                      :prepend-icon="$globals.icons.lock"
                      :label="$t('user.new-password')"
                      :type="showPassword ? 'text' : 'password'"
                      :append-icon="showPassword ? $globals.icons.eye : $globals.icons.eyeOff"
                      :rules="[validators.minLength(8)]"
                      @click:append="showPassword = !showPassword"
                    />
                    <v-text-field
                      v-model="password.newTwo"
                      :prepend-icon="$globals.icons.lock"
                      :label="$t('user.confirm-password')"
                      :rules="[password.newOne === password.newTwo || $t('user.password-must-match')]"
                      validate-on-blur
                      :type="showPassword ? 'text' : 'password'"
                      :append-icon="showPassword ? $globals.icons.eye : $globals.icons.eyeOff"
                      @click:append="showPassword = !showPassword"
                    />
                    <UserPasswordStrength :value="password.newOne" />
                  </v-form>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <BaseButton
                    update
                    :disabled="!passwordsMatch || password.current.length < 0"
                    @click="updatePassword"
                  />
                </v-card-actions>
              </v-card>
            </div>
          </v-slide-x-transition>
        </template>
      </ToggleState>
    </section>
    <section>
      <BaseCardSectionTitle class="mt-10" :title="$tc('profile.preferences')"> </BaseCardSectionTitle>
      <v-checkbox
        v-model="userCopy.advanced"
        class="mt-n4"
        :label="$t('profile.show-advanced-description')"
        @change="updateUser"
      ></v-checkbox>
      <nuxt-link class="mt-5 d-flex flex-column justify-center text-center" :to="`/group`"> {{ $t('profile.looking-for-privacy-settings') }} </nuxt-link>
      <div class="d-flex flex-wrap justify-center mt-5">
        <v-btn outlined class="rounded-xl my-1 mx-1" :to="`/user/profile`" nuxt exact>
          <v-icon left>
            {{ $globals.icons.backArrow }}
          </v-icon>
          {{ $t('profile.back-to-profile') }}
        </v-btn>
      </div>
    </section>
  </v-container>
</template>

<script lang="ts">
import { ref, reactive, defineComponent, computed, useContext, watch, toRefs } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";
import { VForm } from "~/types/vuetify";
import { UserOut } from "~/lib/api/types/user";
import UserPasswordStrength from "~/components/Domain/User/UserPasswordStrength.vue";
import { validators } from "~/composables/use-validators";

export default defineComponent({
  components: {
    UserAvatar,
    UserPasswordStrength,
  },
  middleware: "auth",
  setup() {
    const { $auth } = useContext();
    const user = computed(() => $auth.user as unknown as UserOut);

    watch(user, () => {
      userCopy.value = { ...user.value };
    });

    const userCopy = ref({ ...user.value });

    const api = useUserApi();

    const domUpdatePassword = ref<VForm | null>(null);
    const password = reactive({
      current: "",
      newOne: "",
      newTwo: "",
    });

    const passwordsMatch = computed(() => password.newOne === password.newTwo && password.newOne.length > 0);

    async function updateUser() {
      const { response } = await api.users.updateOne(userCopy.value.id, userCopy.value);
      if (response?.status === 200) {
        $auth.fetchUser();
      }
    }

    async function updatePassword() {
      if (!userCopy.value?.id) {
        return;
      }
      const { response } = await api.users.changePassword({
        currentPassword: password.current,
        newPassword: password.newOne,
      });

      if (response?.status === 200) {
        console.log("Password Changed");
      }
    }

    const state = reactive({
      hideImage: false,
      passwordLoading: false,
      showPassword: false,
      loading: false,
    });

    return {
      ...toRefs(state),
      updateUser,
      updatePassword,
      userCopy,
      password,
      domUpdatePassword,
      passwordsMatch,
      validators,
    };
  },
  head() {
    return {
      title: this.$t("settings.profile") as string,
    };
  },
});
</script>
