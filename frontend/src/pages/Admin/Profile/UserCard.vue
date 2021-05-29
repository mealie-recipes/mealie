<template>
  <StatCard :icon="$globals.icons.user">
    <template v-slot:avatar>
      <v-avatar color="accent" size="120" class="white--text headline mt-n16">
        <img :src="userProfileImage" v-if="!hideImage" @error="hideImage = true" @load="hideImage = false" />
        <div v-else>
          {{ initials }}
        </div>
      </v-avatar>
    </template>
    <template v-slot:after-heading>
      <div class="ml-auto text-right">
        <div class="body-3 grey--text font-weight-light" v-text="$t('user.user-id-with-value', { id: user.id })" />

        <h3 class="display-2 font-weight-light text--primary">
          <small> {{ $t("group.group") }}: {{ user.group }} </small>
        </h3>
      </div>
    </template>
    <template v-slot:actions>
      <BaseDialog
        :title="$t('user.reset-password')"
        title-icon="mdi-lock"
        :submit-text="$t('settings.change-password')"
        @submit="changePassword"
        :loading="loading"
        :top="true"
      >
        <template v-slot:open="{ open }">
          <v-btn color="info" class="mr-1" small @click="open">
            <v-icon left>mdi-lock</v-icon>
            Change Password
          </v-btn>
        </template>

        <v-card-text>
          <v-form ref="passChange">
            <v-text-field
              v-model="password.current"
              prepend-icon="mdi-lock"
              :label="$t('user.current-password')"
              :rules="[existsRule]"
              validate-on-blur
              :type="showPassword ? 'text' : 'password'"
              @click:append="showPassword.current = !showPassword.current"
            ></v-text-field>
            <v-text-field
              v-model="password.newOne"
              prepend-icon="mdi-lock"
              :label="$t('user.new-password')"
              :rules="[minRule]"
              :type="showPassword ? 'text' : 'password'"
              @click:append="showPassword.newOne = !showPassword.newOne"
            ></v-text-field>
            <v-text-field
              v-model="password.newTwo"
              prepend-icon="mdi-lock"
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
    <template v-slot:bottom>
      <v-card-text>
        <v-form ref="userUpdate">
          <v-text-field
            :label="$t('user.username')"
            required
            v-model="user.username"
            :rules="[existsRule]"
            validate-on-blur
          >
          </v-text-field>
          <v-text-field
            :label="$t('user.full-name')"
            required
            v-model="user.fullName"
            :rules="[existsRule]"
            validate-on-blur
          >
          </v-text-field>
          <v-text-field :label="$t('user.email')" :rules="[emailRule]" validate-on-blur required v-model="user.email">
          </v-text-field>
        </v-form>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions class="pb-1 pt-3">
        <TheUploadBtn
          icon="mdi-image-area"
          :text="$t('user.upload-photo')"
          :url="userProfileImage"
          file-name="profile_image"
        />
        <v-spacer></v-spacer>
        <TheButton update @click="updateUser" />
      </v-card-actions>
    </template>
  </StatCard>
</template>

<script>
import BaseDialog from "@/components/UI/Dialogs/BaseDialog";
import StatCard from "@/components/UI/StatCard";
import TheUploadBtn from "@/components/UI/Buttons/TheUploadBtn";
import { api } from "@/api";
import { validators } from "@/mixins/validators";
import { initials } from "@/mixins/initials";
export default {
  components: {
    BaseDialog,
    TheUploadBtn,
    StatCard,
  },
  mixins: [validators, initials],
  data() {
    return {
      hideImage: false,
      passwordLoading: false,
      password: {
        current: "",
        newOne: "",
        newTwo: "",
      },
      showPassword: false,
      loading: false,
      user: {},
    };
  },

  computed: {
    userProfileImage() {
      return `api/users/${this.user.id}/image`;
    },
  },

  async mounted() {
    this.refreshProfile();
  },

  watch: {
    userProfileImage() {
      this.hideImage = false;
    },
  },

  methods: {
    async refreshProfile() {
      this.user = await api.users.self();
    },
    openAvatarPicker() {
      this.showAvatarPicker = true;
    },
    selectAvatar(avatar) {
      this.user.avatar = avatar;
    },
    async updateUser() {
      if (!this.$refs.userUpdate.validate()) {
        return;
      }
      this.loading = true;
      const response = await api.users.update(this.user);
      if (response) {
        this.$store.commit("setToken", response.data.access_token);
        this.refreshProfile();
        this.loading = false;
        this.$store.dispatch("requestUserData");
      }
    },
    async changePassword() {
      this.paswordLoading = true;
      let data = {
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
};
</script>

<style></style>
