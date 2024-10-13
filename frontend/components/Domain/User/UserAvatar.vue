<template>
  <v-tooltip
    v-if="userId"
    :disabled="!user || !tooltip"
    right
  >
    <template #activator="{ on, attrs }">
      <v-list-item-avatar v-if="list" v-bind="attrs" v-on="on">
        <v-img :src="imageURL" :alt="userId" @load="error = false" @error="error = true"> </v-img>
      </v-list-item-avatar>
      <v-avatar v-else :size="size" v-bind="attrs" v-on="on">
        <v-img :src="imageURL" :alt="userId" @load="error = false" @error="error = true"> </v-img>
      </v-avatar>
    </template>
    <span v-if="user">
      {{ user.fullName }}
    </span>
  </v-tooltip>
</template>

<script lang="ts">
import { defineComponent, toRefs, reactive, useContext, computed } from "@nuxtjs/composition-api";
import { useUserStore } from "~/composables/store/use-user-store";
import { UserOut } from "~/lib/api/types/user";

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
    tooltip: {
      type: Boolean,
      default: true,
    }
  },
  setup(props) {
    const state = reactive({
      error: false,
    });

    const { $auth } = useContext();
    const { store: users } = useUserStore();
    const user = computed(() => {
      return users.value.find((user) => user.id === props.userId);
    })

    const imageURL = computed(() => {
      // TODO Setup correct user type for $auth.user
      const authUser = $auth.user as unknown as UserOut | null;
      const key = authUser?.cacheKey ?? "";
      return `/api/media/users/${props.userId}/profile.webp?cacheKey=${key}`;
    });

    return {
      user,
      imageURL,
      ...toRefs(state),
    };
  },
});
</script>
