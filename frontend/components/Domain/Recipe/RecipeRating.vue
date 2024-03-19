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
import { defineComponent, ref, useContext } from "@nuxtjs/composition-api";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useUserApi } from "~/composables/api";
export default defineComponent({
  props: {
    emitOnly: {
      type: Boolean,
      default: false,
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
    const { $auth } = useContext();
    const { isOwnGroup } = useLoggedInState();

    const rating = ref(props.value);

    const api = useUserApi();
    function updateRating(val: number | null) {
      if (!props.emitOnly) {
        api.users.setRating($auth.user?.id || "", props.slug, val || 0, null);
      }
      context.emit("input", val);
    }

    return { isOwnGroup, rating, updateRating };
  },
});
</script>

<style lang="scss" scoped></style>
