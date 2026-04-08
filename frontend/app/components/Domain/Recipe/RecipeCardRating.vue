<template>
  <div class="rating-display">
    <span
      v-for="(star, index) in ratingDisplay"
      :key="index"
      class="star"
      :class="{
        'star-half': star === 'half',
        'text-secondary': !useGroupStyle,
        'text-grey-darken-1': useGroupStyle,
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
import { useLoggedInState } from "~/composables/use-logged-in-state";
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

const { isOwnGroup } = useLoggedInState();
const { userRatings } = useUserSelfRatings();

const userRating = computed(() => {
  return userRatings.value.find(r => r.recipeId === props.recipeId)?.rating ?? undefined;
});

const ratingValue = computed(() => userRating.value || props.modelValue || 0);
const useGroupStyle = computed(() => isOwnGroup.value && !userRating.value && props.modelValue);
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
