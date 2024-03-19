<template>
  <div @click.prevent>
    <v-rating
      :value="rating"
      :readonly="!isOwnGroup"
      color="secondary"
      background-color="secondary lighten-3"
      length="5"
      :dense="small ? true : undefined"
      :size="small ? 15 : undefined"
      hover
      clearable
      @input="updateRating"
      @click="updateRating"
    ></v-rating>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
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

    // prefer user rating over group rating
    const rating = computed(() => {
      if (!ratingsLoaded.value) {
        return;
      }
      if (!($auth.user?.id) || props.preferGroupRating) {
        return props.value;
      }

      const userRating = userRatings.value.find((r) => r.recipeId === props.recipeId);
      return userRating?.rating || props.value;
    });

    function updateRating(val: number | null) {
      if (!isOwnGroup.value) {
        return;
      }

      if (!props.emitOnly) {
        setRating(props.slug, val || 0, null);
      }
      context.emit("input", val);
    }

    return { isOwnGroup, rating, updateRating };
  },
});
</script>

<style lang="scss" scoped></style>
