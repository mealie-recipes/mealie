<template>
  <div @click.prevent>
    <v-rating
      v-model="rating"
      :readonly="!isOwnGroup"
      color="secondary"
      background-color="secondary lighten-3"
      length="5"
      :dense="small ? true : undefined"
      :size="small ? 15 : undefined"
      hover
      :value="value"
      clearable
      @input="updateRating"
      @click="updateRating"
    ></v-rating>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from "@nuxtjs/composition-api";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useUserApi } from "~/composables/api";
export default defineComponent({
  props: {
    emitOnly: {
      type: Boolean,
      default: false,
    },
    // TODO Remove name prop?
    name: {
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

    const rating = ref(props.value);

    const api = useUserApi();
    function updateRating(val: number | null) {
      if (val === 0) {
        val = null;
      }
      if (!props.emitOnly) {
        api.recipes.patchOne(props.slug, {
          rating: val,
        });
      }
      context.emit("input", val);
    }

    return { isOwnGroup, rating, updateRating };
  },
});
</script>

<style lang="scss" scoped></style>
