<template>
  <div @click.prevent>
    <!-- User Rating -->
    <v-hover v-slot="{ hover }">
      <v-rating
        v-if="isOwnGroup && (userRating || hover || !ratingsLoaded)"
        :value="userRating"
        color="secondary"
        background-color="secondary lighten-3"
        length="5"
        :dense="small ? true : undefined"
        :size="small ? 15 : undefined"
        hover
        clearable
        @input="updateRating"
        @click="updateRating"
      />
      <!-- Group Rating -->
      <v-rating
        v-else
        :value="groupRating"
        :half-increments="true"
        :readonly="true"
        color="grey darken-1"
        background-color="secondary lighten-3"
        length="5"
        :dense="small ? true : undefined"
        :size="small ? 15 : undefined"
        hover
      />
    </v-hover>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref, watch } from "@nuxtjs/composition-api";
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
  },
  setup(props, context) {
    const { isOwnGroup } = useLoggedInState();
    const { userRatings, setRating, ready: ratingsLoaded } = useUserSelfRatings();

    const userRating = computed(() => {
      return userRatings.value.find((r) => r.recipeId === props.recipeId)?.rating;
    });

    // if a user unsets their rating, we don't want to fall back to the group rating since it's out of sync
    const hideGroupRating = ref(!!userRating.value);
    watch(
      () => userRating.value,
      () => {
        if (userRating.value) {
          hideGroupRating.value = true;
        }
      },
    )

    const groupRating = computed(() => {
      return hideGroupRating.value ? 0 : props.value;
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

    return {
      isOwnGroup,
      ratingsLoaded,
      groupRating,
      userRating,
      updateRating,
    };
  },
});
</script>

<style lang="scss" scoped></style>
