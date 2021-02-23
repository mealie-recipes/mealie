<template>
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
        <v-text-field label="Full Name" v-model="user.fullName"> </v-text-field>
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
      <v-btn color="accent" class="mr-2">
        <v-icon left> mdi-lock </v-icon>
        {{ $t("settings.change-password") }}
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn color="success" class="mr-2" @click="updateUser">
        <v-icon left> mdi-content-save </v-icon>
        {{ $t("general.save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
// import AvatarPicker from '@/components/AvatarPicker'
import api from "@/api";
export default {
  pageTitle: "My Profile",
  data() {
    return {
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
  },
};
</script>