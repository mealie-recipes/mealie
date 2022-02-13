<template>
  <v-img
    v-if="!fallBackImage"
    :height="height"
    :src="getImage(recipeId)"
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

<script lang="ts">
import { computed, defineComponent, ref, watch } from "@nuxtjs/composition-api";
import { useStaticRoutes, useUserApi } from "~/composables/api";

export default defineComponent({
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
      type: Number,
      default: 200,
    },
  },
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
      }
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
