<template>
  <div @click="$emit('click')">
    <v-img
      :height="height"
      v-if="!fallBackImage"
      :src="getImage(slug)"
      @load="fallBackImage = false"
      @error="fallBackImage = true"
    >
      <slot></slot>
    </v-img>
    <v-icon v-else color="primary" class="icon-position" :size="iconSize">
      mdi-silverware-variant
    </v-icon>
  </div>
</template>

<script>
import { api } from "@/api";
export default {
  props: {
    tiny: {
      type: Boolean,
      default: null,
    },
    small: {
      type: Boolean,
      default: null,
    },
    large: {
      type: Boolean,
      default: null,
    },
    iconSize: {
      default: 100,
    },
    slug: {
      default: null,
    },
    height: {
      default: 200,
    },
  },
  computed: {
    imageSize() {
      if (this.tiny) return "tiny";
      if (this.small) return "small";
      if (this.large) return "large";
      return "large";
    },
  },
  watch: {
    slug() {
      this.fallBackImage = false;
    },
  },
  data() {
    return {
      fallBackImage: false,
    };
  },
  methods: {
    getImage(image) {
      switch (this.imageSize) {
        case "tiny":
          return api.recipes.recipeTinyImage(image);
        case "small":
          return api.recipes.recipeSmallImage(image);
        case "large":
          return api.recipes.recipeImage(image);
      }
    },
  },
};
</script>

<style scoped>
.icon-position {
  opacity: 0.8;
  display: flex !important;
  position: relative;
  margin-left: auto !important;
  margin-right: auto !important;
}
</style>