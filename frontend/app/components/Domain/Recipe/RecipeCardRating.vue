<template>
  <div class="rating-display">
    <span
      v-for="(star, index) in ratingDisplay"
      :key="index"
      class="star"
      :class="{
        'star-half': star === 'half',
        'text-secondary': !showGroupAverage,
        'text-grey-darken-1': showGroupAverage,
      }"
    >
      <!-- We render both the full and empty stars for "half" stars because they're layered over each other -->
      <span
        v-if="star === 'empty' || star === 'half'"
        class="star-empty"
      >
        ☆
      </span>
      <span
        v-if="star === 'full' || star === 'half'"
        class="star-full"
      >
        ★
      </span>
    </span>
  </div>
</template>

<script setup lang="ts">
import { useUserSelfRatings } from "~/composables/use-users";

type Star = "full" | "half" | "empty";

const props = defineProps({
  modelValue: {
    type: Number,
    default: 0,
  },
  recipeId: {
    type: String,
    default: "",
  },
});

const { userRatings } = useUserSelfRatings();

const userRating = computed(() => {
  return userRatings.value.find(r => r.recipeId === props.recipeId)?.rating ?? null;
});

// this display is always readonly, so we show the user's own rating if they have one,
// and otherwise fall back to the group average (in grey), if there is one.
// An unset rating may be null or 0
const showGroupAverage = computed(() => !userRating.value && !!props.modelValue);
const ratingValue = computed(() => (showGroupAverage.value ? props.modelValue : userRating.value) || 0);
const ratingDisplay = computed<Star[]>(
  () => {
    const stars: Star[] = [];

    for (let i = 0; i < 5; i++) {
      const diff = ratingValue.value - i;
      if (diff >= 1) {
        stars.push("full");
      }
      else if (diff >= 0.25) { // round to half star if rating is at least 0.25 but not quite a full star
        stars.push("half");
      }
      else {
        stars.push("empty");
      }
    }

    return stars;
  },
);
</script>

<style lang="scss" scoped>
.rating-display {
  display: inline-flex;
  align-items: center;
  gap: 1px;

  .star {
    font-size: 18px;
    transition: color 0.2s ease;
    user-select: none;
    position: relative;
    display: inline-block;
    &.star-half {
      .star-full {
        position: absolute;
        left: 0;
        top: 0;
        width: 50%;
        overflow: hidden;
      }
    }
  }
}
</style>
