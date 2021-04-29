<template>
  <v-row dense>
    <v-col cols="12" md="8" sm="12">
      <v-card>
        <v-card-title class="headline">
          <span>
            <v-progress-circular
              v-if="loading"
              indeterminate
              color="primary"
              large
              class="mr-2"
            >
            </v-progress-circular>
          </span>
          {{ $t("settings.profile") }}
          <v-spacer></v-spacer>
          {{ $t("user.user-id-with-value", { id: user.id }) }}
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="3" align="center" justify="center">
              <v-avatar
                color="accent"
                size="120"
                class="white--text headline mr-2"
              >
                <img
                  :src="userProfileImage"
                  v-if="!hideImage"
                  @error="hideImage = true"
                />
                <div v-else>
                  {{ initials }}
                </div>
              </v-avatar>
            </v-col>
            <v-col cols="12" md="9">
              <v-form>
                <v-text-field
                  :label="$t('user.full-name')"
                  required
                  v-model="user.fullName"
                  :rules="[existsRule]"
                  validate-on-blur
                >
                </v-text-field>
                <v-text-field
                  :label="$t('user.email')"
                  :rules="[emailRule]"
                  validate-on-blur
                  required
                  v-model="user.email"
                >
                </v-text-field>
                <v-text-field
                  :label="$t('group.group')"
                  readonly
                  v-model="user.group"
                  persistent-hint
                  :hint="$t('group.groups-can-only-be-set-by-administrators')"
                >
                </v-text-field>
              </v-form>
            </v-col>
          </v-row>
        </v-card-text>

        <v-card-actions>
          <TheUploadBtn
            icon="mdi-image-area"
            :text="$t('user.upload-photo')"
            :url="userProfileImage"
            file-name="profile_image"
          />

          <v-spacer></v-spacer>
          <v-btn color="success" class="mr-2" @click="updateUser">
            <v-icon left> mdi-content-save </v-icon>
            {{ $t("general.save") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-col>
    <v-col cols="12" md="4" sm="12">
      <v-card height="100%">
        <v-card-title class="headline">
          {{ $t("user.reset-password") }}
          <v-spacer></v-spacer>
        </v-card-title>
        <v-divider></v-divider>
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
              :rules="[
                password.newOne === password.newTwo ||
                  $t('user.password-must-match'),
              ]"
              validate-on-blur
              :type="showPassword ? 'text' : 'password'"
              @click:append="showPassword.newTwo = !showPassword.newTwo"
            ></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-btn
            icon
            @click="showPassword = !showPassword"
            :loading="passwordLoading"
          >
            <v-icon v-if="!showPassword">mdi-eye-off</v-icon>
            <v-icon v-else> mdi-eye </v-icon>
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn color="accent" class="mr-2" @click="changePassword">
            <v-icon left> mdi-lock </v-icon>
            {{ $t("settings.change-password") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
// import AvatarPicker from '@/components/AvatarPicker'
import TheUploadBtn from "@/components/UI/Buttons/TheUploadBtn";
import { api } from "@/api";
import { validators } from "@/mixins/validators";
import { initials } from "@/mixins/initials";
export default {
  components: {
    TheUploadBtn,
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
      user: {
        fullName: "",
        email: "",
        group: "",
        admin: false,
        id: 0,
      },
    };
  },

  computed: {
    userProfileImage() {
      this.resetImage();
      return `api/users/${this.user.id}/image`;
    },
  },

  async mounted() {
    this.refreshProfile();
  },

  methods: {
    resetImage() {
      this.hideImage = false;
    },
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
      this.loading = true;
      const response = await api.users.update(this.user);
      if(response) {
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

<style>
</style>