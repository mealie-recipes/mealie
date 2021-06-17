<template>
  <v-card>
    <v-card-title class="headline">
      <v-icon large class="mr-2">
        {{ $globals.icons.commentTextMultipleOutline }}
      </v-icon>
      {{ $t("recipe.comments") }}
    </v-card-title>
    <v-divider class="mx-2"></v-divider>
    <v-card class="ma-2" v-for="(comment, index) in comments" :key="comment.id">
      <v-list-item two-line>
        <v-list-item-avatar color="accent" class="white--text">
          <img :src="getProfileImage(comment.user.id)" />
        </v-list-item-avatar>
        <v-list-item-content>
          <v-list-item-title> {{ comment.user.username }}</v-list-item-title>
          <v-list-item-subtitle> {{ $d(new Date(comment.dateAdded), "short") }} </v-list-item-subtitle>
        </v-list-item-content>
        <v-card-actions v-if="loggedIn">
          <TheButton
            small
            minor
            v-if="!editKeys[comment.id] && (user.admin || comment.user.id === user.id)"
            delete
            @click="deleteComment(comment.id)"
          />
          <TheButton
            small
            v-if="!editKeys[comment.id] && comment.user.id === user.id"
            edit
            @click="editComment(comment.id)"
          />
          <TheButton small v-else-if="editKeys[comment.id]" update @click="updateComment(comment.id, index)" />
        </v-card-actions>
      </v-list-item>
      <div>
        <v-card-text>
          {{ !editKeys[comment.id] ? comment.text : null }}
          <v-textarea v-if="editKeys[comment.id]" v-model="comment.text"> </v-textarea>
        </v-card-text>
      </div>
    </v-card>
    <v-card-text v-if="loggedIn">
      <v-textarea auto-grow row-height="1" outlined v-model="newComment"> </v-textarea>
      <div class="d-flex">
        <TheButton class="ml-auto" create @click="createNewComment"> {{ $t("recipe.comment-action") }} </TheButton>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
import { api } from "@/api";
const NEW_COMMENT_EVENT = "new-comment";
const UPDATE_COMMENT_EVENT = "update-comment";
export default {
  props: {
    comments: {
      type: Array,
    },
    slug: {
      type: String,
    },
  },
  data() {
    return {
      newComment: "",
      editKeys: {},
    };
  },
  computed: {
    user() {
      return this.$store.getters.getUserData;
    },
    loggedIn() {
      return this.$store.getters.getIsLoggedIn;
    },
  },
  watch: {
    comments() {
      for (const comment of this.comments) {
        this.$set(this.editKeys, comment.id, false);
      }
    },
  },
  methods: {
    resetImage() {
      this.hideImage == false;
    },
    getProfileImage(id) {
      return api.users.userProfileImage(id);
    },
    editComment(id) {
      this.$set(this.editKeys, id, true);
    },
    async updateComment(id, index) {
      this.$set(this.editKeys, id, false);

      await api.recipes.updateComment(this.slug, id, this.comments[index]);
      this.$emit(UPDATE_COMMENT_EVENT);
    },
    async createNewComment() {
      await api.recipes.createComment(this.slug, { text: this.newComment });
      this.$emit(NEW_COMMENT_EVENT);

      this.newComment = "";
    },
    async deleteComment(id) {
      await api.recipes.deleteComment(this.slug, id);
      this.$emit(UPDATE_COMMENT_EVENT);
    },
  },
};
</script>

<style lang="scss" scoped>
</style>