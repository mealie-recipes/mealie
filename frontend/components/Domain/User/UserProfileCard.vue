<template>
  <BaseStatCard :icon="$globals.icons.user" color="accent">
    <template #after-heading>
      <div class="ml-auto text-right">
        <div class="body-3 grey--text font-weight-light" v-text="$t('user.user-id-with-value', { id: user.id })" />

        <h3 class="display-2 font-weight-light text--primary">
          <small> {{ $t("group.group-with-value", { groupID: user.group }) }}</small>
        </h3>
      </div>
    </template>

    <!-- Change Password -->
    <template #actions>
      <BaseDialog
        :title="$t('user.reset-password')"
        :title-icon="$globals.icons.lock"
        :submit-text="$t('settings.change-password')"
        :loading="loading"
        :top="true"
        @submit="updatePassword"
      >
        <template #activator="{ open }">
          <v-btn color="info" class="mr-1" small @click="open">
            <v-icon left>{{ $globals.icons.lock }}</v-icon>
            {{ $t("settings.change-password") }}
          </v-btn>
        </template>

        <v-card-text>
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
      </BaseDialog>
    </template>

    <!-- Update User -->
    <template #bottom>
      <v-card-text>
        <v-form ref="userUpdate">
          <v-text-field v-model="userCopy.username" :label="$t('user.username')" required validate-on-blur>
          </v-text-field>
          <v-text-field v-model="userCopy.fullName" :label="$t('user.full-name')" required validate-on-blur>
          </v-text-field>
          <v-text-field v-model="userCopy.email" :label="$t('user.email')" validate-on-blur required> </v-text-field>
        </v-form>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions class="pb-1 pt-3">
        <AppButtonUpload :icon="$globals.icons.fileImage" :text="$t('user.upload-photo')" file-name="profile_image" />
        <v-spacer></v-spacer>
        <BaseButton update @click="updateUser" />
      </v-card-actions>
    </template>
  </BaseStatCard>
</template>

<script lang="ts">
import { ref, reactive, defineComponent } from "@nuxtjs/composition-api";
import { useApiSingleton } from "~/composables/use-api";
const events = {
  UPDATE_USER: "update",
  CHANGE_PASSWORD: "change-password",
  UPLOAD_PHOTO: "upload-photo",
  REFRESH: "refresh",
};

export default defineComponent({
  props: {
    user: {
      type: Object,
      required: true,
    },
  },
  setup(props, context) {
    const userCopy = ref({ ...props.user });
    const api = useApiSingleton();

    const domUpdatePassword = ref<VForm | null>(null);
    const password = reactive({
      current: "",
      newOne: "",
      newTwo: "",
    });

    async function updateUser() {
      const { response } = await api.users.updateOne(userCopy.value.id, userCopy.value);
      if (response?.status === 200) {
        context.emit(events.REFRESH);
      }
    }

    async function updatePassword() {
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

  methods: {
    // async updateUser() {
    //   if (!this.$refs.userUpdate.validate()) {
    //     return;
    //   }
    //   this.loading = true;
    //   const response = await api.users.update(this.user);
    //   if (response) {
    //     this.$store.commit("setToken", response.data.access_token);
    //     this.refreshProfile();
    //     this.loading = false;
    //     this.$store.dispatch("requestUserData");
    //   }
    // },
    async changePassword() {
      this.paswordLoading = true;
      const data = {
        currentPassword: this.password.current,
        newPassword: this.password.newOne,
      };

      if (this.$refs.passChange.validate()) {
        if (await api.users.changePassword(this.user.id, data)) {
          this.$emit("refresh");
        }
      }
      this.paswordLoading = false;
    },
  },
});
</script>

<style></style>
