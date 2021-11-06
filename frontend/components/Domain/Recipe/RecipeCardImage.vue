<template>
  <v-img
    v-if="!fallBackImage"
    :height="height"
    :src="getImage(slug)"
    @click="$emit('click')"
    @load="fallBackImage = false"
    @error="fallBackImage = true"
  >
    <slot> </slot>
  </v-img>
  <div v-else class="icon-slot" @click="$emit('click')">
    <v-icon color="primary" class="icon-position" :size="iconSize">
      {{ $globals.icons.primary }}
    </v-icon>
    <slot> </slot>
  </div>
</template>

<script>
import { useStaticRoutes, useUserApi } from "~/composables/api";
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
      type: [Number, String],
      default: 100,
    },
    slug: {
      type: String,
      default: null,
    },
    imageVersion: {
      type: String,
      default: null,
    },
    height: {
      type: Number,
      default: 200,
    },
  },
  setup() {
    const api = useUserApi();

    const { recipeImage, recipeSmallImage, recipeTinyImage } = useStaticRoutes();

    return { api, recipeImage, recipeSmallImage, recipeTinyImage };
  },
  data() {
    return {
      fallBackImage: false,
    };
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
  methods: {
    getImage(slug) {
      switch (this.imageSize) {
        case "tiny":
          return this.recipeTinyImage(slug, this.imageVersion);
        case "small":
          return this.recipeSmallImage(slug, this.imageVersion);
        case "large":
          return this.recipeImage(slug, this.imageVersion);
      }
    },
  },
};
</script>

<style scoped>
.icon-slot {
  position: relative;
}

.icon-slot > div {
  top: 0;
  position: absolute;
  z-index: 1;
}

.icon-position {
  opacity: 0.8;
  display: flex !important;
  position: relative;
  margin-left: auto !important;
  margin-right: auto !important;
}
</style>