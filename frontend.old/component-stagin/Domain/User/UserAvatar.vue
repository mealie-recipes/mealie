<template>
  <v-list-item two-line to="/admin/profile">
    <v-list-item-avatar color="accent" class="white--text">
      <v-img v-if="!noImage" :src="profileImage" />
      <div v-else>
        {{ initials }}
      </div>
    </v-list-item-avatar>

    <v-list-item-content>
      <v-list-item-title> {{ user.fullName }}</v-list-item-title>
      <v-list-item-subtitle> {{ user.admin ? $t("user.admin") : $t("user.user") }}</v-list-item-subtitle>
    </v-list-item-content>
  </v-list-item>
</template>

<script>
import { initials } from "@/mixins/initials";
import axios from "axios";
import { api } from "@/api";
export default {
  mixins: [initials],
  props: {
    user: {
      type: Object,
    },
  },
  data() {
    return {
      noImage: false,
      profileImage: "",
    };
  },
  watch: {
    async user() {
      this.setImage();
    },
  },
  methods: {
    async setImage() {
      const userImageURL = api.users.userProfileImage(this.user.id);
      if (await this.imageExists(userImageURL)) {
        this.noImage = false;
        this.profileImage = userImageURL;
      } else {
        this.noImage = true;
      }
    },
    async imageExists(url) {
      const response = await axios.get(url).catch(() => {
        this.noImage = true;
        return { status: 404 };
      });
      return response.status !== 404;
    },
  },
};
</script>

<style lang="scss" scoped>
</style>