<template>
  <v-card>
    <v-card-title class="headline">
      <span>
        <v-avatar color="accent" size="40" class="mr-2">
          <img src="https://cdn.vuetifyjs.com/images/john.jpg" alt="John" />
        </v-avatar>
      </span>
      Profile
    </v-card-title>
    <v-divider></v-divider>
    <v-card-text>
      <v-form>
        <v-text-field label="Full Name"> </v-text-field>
        <v-text-field label="Email"> </v-text-field>
        <v-text-field label="Group" readonly> </v-text-field>
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-btn color="accent" class="mr-2">
        <v-icon left> mdi-lock </v-icon>
        {{ $t("settings.change-password") }}
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn color="success" class="mr-2">
        <v-icon left> mdi-content-save </v-icon>
        {{ $t("general.save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
// import AvatarPicker from '@/components/AvatarPicker'
export default {
  pageTitle: "My Profile",
  data() {
    return {
      loading: false,
      form: {
        firstName: "John",
        lastName: "Doe",
        contactEmail: "john@doe.com",
        avatar: "MALE_CAUCASIAN_BLOND_BEARD",
      },
      showAvatarPicker: false,
    };
  },

  methods: {
    openAvatarPicker() {
      this.showAvatarPicker = true;
    },
    selectAvatar(avatar) {
      this.form.avatar = avatar;
    },
  },
};
</script>