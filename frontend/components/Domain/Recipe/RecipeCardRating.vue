<template>
  <div class="rating-display">
    <span
      v-for="(star, index) in ratingDisplay"
      :key="index"
      class="star"
      :class="{
        'full': star === 'full',
        'half': star === 'half',
        'empty': star === 'empty',
        'text-secondary': !useSecondaryStyle,
        'text-grey-darken-1': useSecondaryStyle,
      }"
    >
      <span v-if="star === 'half'" class="star-background">☆</span>
      <span v-if="star === 'half'" class="star-overlay">★</span>
      <span v-else>{{ star === 'empty' ? '☆' : '★' }}</span>
    </span>
  </div>
</template>

<script lang="ts">
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useUserSelfRatings } from "~/composables/use-users";

type Star = "full" | "half" | "empty";

export default defineNuxtComponent({
  props: {
    modelValue: {
      type: Number,
      default: 0,
    },
    recipeId: {
      type: String,
      default: "",
    },
  },
  emits: ["update:modelValue"],
  setup(props) {
    const { isOwnGroup } = useLoggedInState();
    const { userRatings } = useUserSelfRatings();

    const userRating = computed(() => {
      return userRatings.value.find(r => r.recipeId === props.recipeId)?.rating ?? undefined;
    });

    const ratingValue = computed(() => userRating.value || props.modelValue || 0);
    const useSecondaryStyle = computed(() => isOwnGroup.value && !userRating.value && props.modelValue);
    const ratingDisplay = computed<Star[]>(
      () => {
        const stars: Star[] = [];

        for (let i = 0; i < 5; i++) {
          const diff = ratingValue.value - i;
          if (diff >= 1) {
            stars.push("full");
          }
          else if (diff >= 0.25) {
            stars.push("half");
          }
          else {
            stars.push("empty");
          }
        }

        return stars;
      },
    );

    return {
      ratingValue,
      useSecondaryStyle,
      ratingDisplay,
    };
  },
});
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

    &.empty {
      color: rgb(var(--v-theme-secondary-lighten-3));
    }

    &.full {
      color: rgb(var(--v-theme-secondary));
    }

    &.half {
      .star-overlay {
        position: absolute;
        left: 0;
        top: 0;
        width: 50%;
        overflow: hidden;
        color: rgb(var(--v-theme-secondary));
      }
    }

    /* Group rating when a user is logged-in and hasn't rated this recipe */
    &.text-grey-darken-1.full {
      color: rgb(var(--v-theme-grey-darken-1));
    }

    &.text-grey-darken-1.half {
      .star-overlay {
        color: rgb(var(--v-theme-grey-darken-1));
      }
    }
  }
}
</style>
