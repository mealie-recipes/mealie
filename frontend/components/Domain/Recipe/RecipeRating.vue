<template>
  <div @click.prevent>
    <v-rating
      v-model="rating"
      :readonly="!loggedIn"
      color="secondary"
      background-color="secondary lighten-3"
      length="5"
      :dense="small ? true : undefined"
      :size="small ? 15 : undefined"
      hover
      :value="value"
      @input="updateRating"
      @click="updateRating"
    ></v-rating>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useContext } from "@nuxtjs/composition-api";
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
    const { $auth } = useContext();
    const loggedIn = computed(() => {
      return $auth.loggedIn;
    });

    const rating = ref(props.value);

    const api = useUserApi();
    function updateRating(val: number) {
      if (props.emitOnly) {
        context.emit("input", val);
        return;
      }
      api.recipes.patchOne(props.slug, {
        rating: val,
      });
    }

    return { loggedIn, rating, updateRating };
  },
});
</script>

<style lang="scss" scoped></style>
