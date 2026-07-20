<template>
  <div @click.prevent>
    <!-- User Rating: shows the group average until the user rates the recipe themselves -->
    <v-rating
      v-if="isOwnGroup"
      :model-value="displayRating"
      :active-color="showGroupAverage ? 'grey-darken-1' : 'secondary'"
      color="secondary-lighten-3"
      length="5"
      :half-increments="showGroupAverage"
      :density="small ? 'compact' : 'default'"
      :size="small ? 'x-small' : undefined"
      :hover="canHover"
      :clearable="!!userRatingDisplayValue"
      @update:model-value="updateRating(+$event)"
    />
    <!-- Group Rating -->
    <v-rating
      v-else
      :model-value="groupRating"
      :half-increments="true"
      active-color="grey-darken-1"
      color="secondary-lighten-3"
      length="5"
      :density="small ? 'compact' : 'default'"
      :size="small ? 'x-small' : undefined"
      readonly
    />
  </div>
</template>

<script setup lang="ts">
import { useMediaQuery } from "@vueuse/core";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useUserSelfRatings } from "~/composables/use-users";

interface Props {
  emitOnly?: boolean;
  recipeId?: string;
  slug?: string;
  small?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  emitOnly: false,
  recipeId: "",
  slug: "",
  small: false,
});

const modelValue = defineModel<number>({ default: 0 });
const groupRating = computed(() => modelValue.value);

const { isOwnGroup } = useLoggedInState();
const { userRatings, setRating } = useUserSelfRatings();

// on touch devices a tap fires mouseenter without a matching mouseleave, which leaves v-rating
// rendering the stuck hover value instead of the model value
const canHover = useMediaQuery("(hover: hover) and (pointer: fine)");

const userRating = computed<number | null>(() => {
  return userRatings.value.find(r => r.recipeId === props.recipeId)?.rating ?? null;
});

const localUserRating = ref(userRating.value);

// while a write is in flight a refetch may still report the pre-click value, so ignore it
const pendingWrites = ref(0);
watch(userRating, (value) => {
  if (!pendingWrites.value) {
    localUserRating.value = value;
  }
});

const userRatingDisplayValue = computed(() => localUserRating.value ?? 0);
const showGroupAverage = computed(() => localUserRating.value === null);

const displayRating = computed(() => {
  return showGroupAverage.value ? groupRating.value : userRatingDisplayValue.value;
});

async function updateRating(val?: number) {
  if (!isOwnGroup.value) {
    return;
  }

  // the group average can be a half value, but user ratings are always whole stars
  let rating = Math.round(val ?? 0);
  if (rating === localUserRating.value) {
    rating = 0;
  }

  localUserRating.value = rating;

  if (props.emitOnly) {
    modelValue.value = rating;
    return;
  }

  pendingWrites.value++;
  try {
    await setRating(props.slug, rating, null);
  }
  finally {
    pendingWrites.value--;
  }
}
</script>

<style lang="scss" scoped></style>
