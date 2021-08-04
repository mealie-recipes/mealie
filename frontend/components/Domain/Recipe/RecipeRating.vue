<template>
  <div @click.prevent>
    <v-rating
      v-model="rating"
      :readonly="!loggedIn"
      color="secondary"
      background-color="secondary lighten-3"
      length="5"
      :dense="small ? true : undefined"
      :size="small ? 15 : undefined"
      hover
      :value="value"
      @input="updateRating"
      @click="updateRating"
    ></v-rating>
  </div>
</template>

<script>
import { defineComponent } from "@nuxtjs/composition-api";
import { useApiSingleton } from "~/composables/use-api";
export default defineComponent({
  props: {
    emitOnly: {
      type: Boolean,
      default: false,
    },
    name: {
      type: String,
      default: "",
    },
    slug: {
      type: String,
      default: "",
    },
    value: {
      type: Number,
      default: 0,
    },
    small: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const api = useApiSingleton();

    return { api };
  },
  data() {
    return {
      rating: 0,
    };
  },
  computed: {
    loggedIn() {
      return this.$auth.loggedIn;
    },
  },
  mounted() {
    this.rating = this.value;
  },
  methods: {
    updateRating(val) {
      if (this.emitOnly) {
        this.$emit("input", val);
        return;
      }
      this.api.recipes.patchOne(this.slug, {
        name: this.name,
        slug: this.slug,
        rating: val,
      });
    },
  },
});
</script>

<style lang="scss" scoped></style>
