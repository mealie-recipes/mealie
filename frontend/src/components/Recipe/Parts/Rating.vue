<template>
  <div @click.prevent>
    <v-rating
      :readonly="!loggedIn"
      color="secondary"
      background-color="secondary lighten-3"
      length="5"
      :dense="small ? true : undefined"
      :size="small ? 15 : undefined"
      hover
      v-model="rating"
      :value="value"
      @input="updateRating"
      @click="updateRating"
    ></v-rating>
  </div>
</template>

<script>
import { api } from "@/api";
export default {
  props: {
    emitOnly: {
      default: false,
    },
    name: String,
    slug: String,
    value: Number,
    small: {
      default: false,
    },
  },
  mounted() {
    this.rating = this.value;
  },
  data() {
    return {
      rating: 0,
    };
  },
  computed: {
    loggedIn() {
      return this.$store.getters.getIsLoggedIn;
    },
  },
  methods: {
    updateRating(val) {
      if (this.emitOnly) {
        this.$emit("input", val);
        return;
      }
      api.recipes.patch({
        name: this.name,
        slug: this.slug,
        rating: val,
      });
    },
  },
};
</script>

<style lang="scss" scoped></style>
