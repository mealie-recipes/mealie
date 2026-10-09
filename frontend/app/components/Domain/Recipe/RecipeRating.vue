<template>
  <div @click.prevent>
    <v-rating
      :model-value="displayRating"
      :active-color="showGroupAverage ? 'grey-darken-1' : 'secondary'"
      color="secondary-lighten-3"
      length="5"
      :half-increments="showGroupAverage"
      :density="small ? 'compact' : 'default'"
      :size="small ? 'x-small' : undefined"
      :readonly="isReadonly"
      :hover="!isReadonly && canHover"
      :clearable="!!displayRating"
      @update:model-value="updateRating(+$event)"
    />
  </div>
</template>

<script setup lang="ts">
import { useMediaQuery } from "@vueuse/core";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useUserSelfRatings } from "~/composables/use-users";

interface Props {
  readonly?: boolean;
  recipeId?: string;
  slug?: string;
  small?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false,
  recipeId: "",
  slug: "",
  small: false,
});

const groupRating = defineModel<number>({ default: 0 });

const { isOwnGroup } = useLoggedInState();
const isReadonly = computed(() => props.readonly || !isOwnGroup.value);
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

// only fall back to the group average when we can't offer the user their own rating,
// and only when there's actually a group average to show. An unset rating may be null or 0
const showGroupAverage = computed(() => {
  return isReadonly.value && !localUserRating.value && !!groupRating.value;
});

const displayRating = computed(() => {
  return showGroupAverage.value ? groupRating.value : (localUserRating.value || 0);
});

async function updateRating(val?: number) {
  if (isReadonly.value) {
    return;
  }

  // user ratings are always whole stars
  let rating = Math.round(val ?? 0);
  if (rating === localUserRating.value) {
    rating = 0;
  }

  localUserRating.value = rating;

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
