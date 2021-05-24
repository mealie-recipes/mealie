<template>
  <v-img
    @click="$emit('click')"
    :height="height"
    v-if="!fallBackImage"
    :src="getImage(slug)"
    @load="fallBackImage = false"
    @error="fallBackImage = true"
  >
    <slot> </slot>
  </v-img>
  <div class="icon-slot" v-else @click="$emit('click')">
    <div>
      <slot> </slot>
    </div>
    <v-icon color="primary" class="icon-position" :size="iconSize">
      {{ $globals.icons.primary }}
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
    imageVersion: {
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
    getImage(slug) {
      switch (this.imageSize) {
        case "tiny":
          return api.recipes.recipeTinyImage(slug, this.imageVersion);
        case "small":
          return api.recipes.recipeSmallImage(slug, this.imageVersion);
        case "large":
          return api.recipes.recipeImage(slug, this.imageVersion);
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