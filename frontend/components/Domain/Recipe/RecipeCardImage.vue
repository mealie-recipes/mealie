<template>
  <v-img
    v-if="!fallBackImage"
    :height="height"
    cover
    min-height="125"
    max-height="fill-height"
    :src="getImage(recipeId)"
    @click="$emit('click')"
    @load="fallBackImage = false"
    @error="fallBackImage = true"
  >
    <slot />
  </v-img>
  <div
    v-else
    class="icon-slot"
    @click="$emit('click')"
  >
    <v-icon
      color="primary"
      class="icon-position"
      :size="iconSize"
    >
      {{ $globals.icons.primary }}
    </v-icon>
    <slot />
  </div>
</template>

<script lang="ts">
import { useStaticRoutes, useUserApi } from "~/composables/api";

export default defineNuxtComponent({
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
    recipeId: {
      type: String,
      required: true,
    },
    imageVersion: {
      type: String,
      default: null,
    },
    height: {
      type: [Number, String],
      default: "100%",
    },
  },
  emits: ["click"],
  setup(props) {
    const api = useUserApi();

    const { recipeImage, recipeSmallImage, recipeTinyImage } = useStaticRoutes();

    const fallBackImage = ref(false);
    const imageSize = computed(() => {
      if (props.tiny) return "tiny";
      if (props.small) return "small";
      if (props.large) return "large";
      return "large";
    });

    watch(
      () => props.recipeId,
      () => {
        fallBackImage.value = false;
      },
    );

    function getImage(recipeId: string) {
      switch (imageSize.value) {
        case "tiny":
          return recipeTinyImage(recipeId, props.imageVersion);
        case "small":
          return recipeSmallImage(recipeId, props.imageVersion);
        case "large":
          return recipeImage(recipeId, props.imageVersion);
      }
    }

    return {
      api,
      fallBackImage,
      imageSize,
      getImage,
    };
  },
});
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
