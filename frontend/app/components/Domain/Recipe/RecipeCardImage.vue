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

<script setup lang="ts">
import { useStaticRoutes } from "~/composables/api";

interface Props {
  tiny?: boolean | null;
  small?: boolean | null;
  large?: boolean | null;
  iconSize?: number | string;
  slug?: string | null;
  recipeId: string;
  imageVersion?: string | null;
  height?: number | string;
}
const props = withDefaults(defineProps<Props>(), {
  tiny: null,
  small: null,
  large: null,
  iconSize: 100,
  slug: null,
  imageVersion: null,
  height: "100%",
});

defineEmits<{
  click: [];
}>();

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
