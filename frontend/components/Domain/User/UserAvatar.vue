<template>
  <v-list-item-avatar v-if="list && userId">
    <v-img :src="imageURL" :alt="userId" @load="error = false" @error="error = true"> </v-img>
  </v-list-item-avatar>
  <v-avatar v-else-if="userId" :size="size">
    <v-img :src="imageURL" :alt="userId" @load="error = false" @error="error = true"> </v-img>
  </v-avatar>
</template>

<script lang="ts">
import { defineComponent, toRefs, reactive, useContext, computed } from "@nuxtjs/composition-api";
import { UserOut } from "~/types/api-types/user";

export default defineComponent({
  props: {
    userId: {
      type: String,
      required: true,
    },
    list: {
      type: Boolean,
      default: false,
    },
    size: {
      type: String,
      default: "42",
    },
  },
  setup(props) {
    const state = reactive({
      error: false,
    });

    const { $auth } = useContext();

    const imageURL = computed(() => {
      // TODO Setup correct user type for $auth.user
      const user = $auth.user as unknown as (UserOut | null);
      const key = user?.cacheKey ?? "";
      return `/api/media/users/${props.userId}/profile.webp?cacheKey=${key}`;
    });

    return {
      imageURL,
      ...toRefs(state),
    };
  },
});
</script>
