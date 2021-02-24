<template>
  <v-row dense>
    <v-col cols="12" md="12" sm="12">
      <v-card>
        <v-card-title class="headline">
          <span>
            <v-avatar color="accent" size="40" class="mr-2" v-if="!loading">
              <img src="https://cdn.vuetifyjs.com/images/john.jpg" alt="John" />
            </v-avatar>
            <v-progress-circular
              v-else
              indeterminate
              color="primary"
              large
              class="mr-2"
            >
            </v-progress-circular>
          </span>
          Profile
          <v-spacer></v-spacer>
          User ID: {{ user.id }}
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-form>
            <v-text-field label="Full Name" v-model="user.fullName">
            </v-text-field>
            <v-text-field label="Email" v-model="user.email"> </v-text-field>
            <v-text-field
              label="Family"
              readonly
              v-model="user.family"
              persistent-hint
              hint="Family groups can only be set by administrators"
            >
            </v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="success" class="mr-2" @click="updateUser">
            <v-icon left> mdi-content-save </v-icon>
            {{ $t("general.save") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-col>
    <v-col cols="12" md="4" sm="12">
      <v-card>
        <v-card-title class="headline">
          Reset Password
          <v-spacer></v-spacer>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-form>
            <v-text-field
              v-model="password.current"
              light="light"
              prepend-icon="mdi-lock"
              label="Current Password"
              :type="showPassword.current ? 'text' : 'password'"
              :append-icon="showPassword.current ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append="showPassword.current = !showPassword.current"
            ></v-text-field>
            <v-text-field
              v-model="password.newOne"
              light="light"
              prepend-icon="mdi-lock"
              label="New Password"
              :type="showPassword.newOne ? 'text' : 'password'"
              :append-icon="showPassword.newOne ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append="showPassword.newOne = !showPassword.newOne"
            ></v-text-field>
            <v-text-field
              v-model="password.newTwo"
              light="light"
              prepend-icon="mdi-lock"
              label="Confirm Password"
              :type="showPassword.newTwo ? 'text' : 'password'"
              :append-icon="showPassword.newTwo ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append="showPassword.newTwo = !showPassword.newTwo"
            ></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
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
import api from "@/api";
export default {
  pageTitle: "My Profile",
  data() {
    return {
      password: {
        current: "",
        newOne: "",
        newTwo: "",
      },
      showPassword: {
        current: false,
        newOne: false,
        newTwo: false,
      },
      loading: false,
      user: {
        fullName: "Change Me",
        email: "changeme@email.com",
        family: "public",
        admin: true,
        id: 1,
      },
      showAvatarPicker: false,
    };
  },

  async mounted() {
    this.refreshProfile();
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
      this.loading = true;
      let newKey = await api.users.update(this.user);
      this.$store.commit("setToken", newKey.access_token);
      this.refreshProfile();
      this.loading = false;
    },
    async changePassword() {
      let data = {
        currentPassword: this.password.current,
        newPassword: this.password.newOne,
      };

      await api.users.changePassword(this.user.id, data);
    },
  },
};
</script>