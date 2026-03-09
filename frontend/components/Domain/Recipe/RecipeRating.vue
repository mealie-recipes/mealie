<template>
  <div @click.prevent>
    <!-- User Rating -->
    <v-hover v-slot="{ isHovering, props: hoverProps }">
      <v-rating
        v-if="isOwnGroup && (userRating || isHovering || !ratingsLoaded)"
        v-bind="hoverProps"
        :model-value="userRating"
        active-color="secondary"
        color="secondary-lighten-3"
        length="5"
        :density="small ? 'compact' : 'default'"
        :size="small ? 'x-small' : undefined"
        hover
        clearable
        @update:model-value="updateRating(+$event)"
      />
      <!-- Group Rating -->
      <v-rating
        v-else
        v-bind="hoverProps"
        :model-value="groupRating"
        :half-increments="true"
        active-color="grey-darken-1"
        color="secondary-lighten-3"
        length="5"
        :density="small ? 'compact' : 'default'"
        :size="small ? 'x-small' : undefined"
        hover
      />
    </v-hover>
  </div>
</template>

<script setup lang="ts">
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useUserSelfRatings } from "~/composables/use-users";

interface Props {
  emitOnly?: boolean;
  recipeId?: string;
  slug?: string;
  small?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  emitOnly: false,
  recipeId: "",
  slug: "",
  small: false,
});

const modelValue = defineModel<number>({ default: 0 });

const { isOwnGroup } = useLoggedInState();
const { userRatings, setRating, ready: ratingsLoaded } = useUserSelfRatings();

const userRating = computed(() => {
  return userRatings.value.find(r => r.recipeId === props.recipeId)?.rating ?? undefined;
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
);

const groupRating = computed(() => {
  return hideGroupRating.value ? 0 : modelValue.value;
});

function updateRating(val?: number) {
  if (!isOwnGroup.value) {
    return;
  }

  if (val === userRating.value) {
    val = 0;
  }

  if (!props.emitOnly) {
    setRating(props.slug, val || 0, null);
  }
  modelValue.value = val ?? 0;
}
</script>

<style lang="scss" scoped></style>
