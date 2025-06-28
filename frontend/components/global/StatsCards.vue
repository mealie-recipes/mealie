<template>
  <v-card
    :min-width="minWidth"
    :to="to"
    :hover="to ? true : false"
  >
    <div class="d-flex flex-no-wrap">
      <v-avatar
        class="ml-3 mr-0 mt-3"
        color="primary"
        size="36"
      >
        <v-icon
          color="white"
          class="pa-1"
          size="x-large"
        >
          {{ activeIcon }}
        </v-icon>
      </v-avatar>
      <div>
        <v-card-title class="text-subtitle-1 pt-2 pb-2">
          <slot name="title" />
        </v-card-title>
        <v-card-subtitle class="pb-2">
          <slot name="value" />
        </v-card-subtitle>
      </div>
    </div>
  </v-card>
</template>

<script lang="ts">
export default defineNuxtComponent({
  props: {
    icon: {
      type: String,
      default: null,
    },
    minWidth: {
      type: String,
      default: "",
    },
    to: {
      type: String,
      default: null,
    },
  },
  setup(props) {
    const { $globals } = useNuxtApp();

    const activeIcon = computed(() => {
      return props.icon ?? $globals.icons.primary;
    });

    return {
      activeIcon,
    };
  },
});
</script>

<style scoped></style>
