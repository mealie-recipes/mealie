<template>
  <v-tooltip
    v-if="userId"
    :disabled="!user || !tooltip"
    location="end"
  >
    <template #activator="{ props: tooltipProps }">
      <v-avatar
        v-if="list"
        v-bind="tooltipProps"
      >
        <v-img
          :src="imageURL"
          :alt="userId"
          @load="error = false"
          @error="error = true"
        />
      </v-avatar>
      <v-avatar
        v-else
        :size="size"
        v-bind="tooltipProps"
      >
        <v-img
          :src="imageURL"
          :alt="userId"
          @load="error = false"
          @error="error = true"
        />
      </v-avatar>
    </template>
    <span v-if="user">
      {{ user.fullName }}
    </span>
  </v-tooltip>
</template>

<script setup lang="ts">
import { useUserStore } from "~/composables/store/use-user-store";

const props = defineProps({
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
  },
});

const error = ref(false);

const auth = useMealieAuth();
const { store: users } = useUserStore();
const user = computed(() => {
  return users.value.find(user => user.id === props.userId);
});

const imageURL = computed(() => {
  // Note: auth.user is a ref now
  const authUser = auth.user.value;
  const key = authUser?.cacheKey ?? "";
  return `/api/media/users/${props.userId}/profile.webp?cacheKey=${key}`;
});
</script>
