<template>
  <div @click.prevent>
    <v-hover v-slot="{ hover }">
      <v-rating
        :value="rating.ratingValue"
        :half-increments="(!hover) || (!isOwnGroup)"
        :readonly="!isOwnGroup"
        :color="hover ? attrs.hoverColor : attrs.color"
        :background-color="attrs.backgroundColor"
        length="5"
        :dense="small ? true : undefined"
        :size="small ? 15 : undefined"
        hover
        clearable
        @input="updateRating"
        @click="updateRating"
      />
    </v-hover>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useContext, watch } from "@nuxtjs/composition-api";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useUserSelfRatings } from "~/composables/use-users";
export default defineComponent({
  props: {
    emitOnly: {
      type: Boolean,
      default: false,
    },
    recipeId: {
      type: String,
      default: "",
    },
    slug: {
      type: String,
      default: "",
    },
    value: {
      type: Number,
      default: 0,
    },
    small: {
      type: Boolean,
      default: false,
    },
    preferGroupRating: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, context) {
    const { $auth } = useContext();
    const { isOwnGroup } = useLoggedInState();
    const { userRatings, setRating, ready: ratingsLoaded } = useUserSelfRatings();
    const hideGroupRating = ref(false);

    type Rating = {
      ratingValue: number | undefined;
      hasUserRating: boolean | undefined
    };

    // prefer user rating over group rating
    const rating = computed<Rating>(() => {
      if (!ratingsLoaded.value) {
        return { ratingValue: undefined, hasUserRating: undefined };
      }
      if (!($auth.user?.id) || props.preferGroupRating) {
        return { ratingValue: props.value, hasUserRating: false };
      }

      const userRating = userRatings.value.find((r) => r.recipeId === props.recipeId);
      return {
        ratingValue: userRating?.rating || (hideGroupRating.value ? 0 : props.value),
        hasUserRating: !!userRating?.rating
      };
    });

    // if a user unsets their rating, we don't want to fall back to the group rating since it's out of sync
    watch(
      () => rating.value.hasUserRating,
      () => {
        if (rating.value.hasUserRating && !props.preferGroupRating) {
          hideGroupRating.value = true;
        }
      },
    )

    const attrs = computed(() => {
      return isOwnGroup.value ? {
        // Logged-in user
        color: rating.value.hasUserRating ? "secondary" : "grey darken-1",
        hoverColor: "secondary",
        backgroundColor: "secondary lighten-3",
      } : {
        // Anonymous user
        color: "secondary",
        hoverColor: "secondary",
        backgroundColor: "secondary lighten-3",
      };
    })

    function updateRating(val: number | null) {
      if (!isOwnGroup.value) {
        return;
      }

      if (!props.emitOnly) {
        setRating(props.slug, val || 0, null);
      }
      context.emit("input", val);
    }

    return {
      attrs,
      isOwnGroup,
      rating,
      updateRating,
    };
  },
});
</script>

<style lang="scss" scoped></style>
