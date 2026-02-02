<template>
  <v-menu
    offset-y
    start
    :bottom="!menuTop"
    :nudge-bottom="!menuTop ? '5' : '0'"
    :top="menuTop"
    :nudge-top="menuTop ? '5' : '0'"
    allow-overflow
    close-delay="125"
    content-class="d-print-none"
  >
    <template #activator="{ props }">
      <v-btn
        :class="{ 'rounded-circle': fab }"
        :small="fab"
        :color="color"
        :icon="!fab"
        dark
        v-bind="props"
        @click.prevent
      >
        <v-icon>{{ $globals.icons.dotsVertical }}</v-icon>
      </v-btn>
    </template>
    <v-list density="compact">
      <v-list-item
        v-for="(item, index) in items"
        :key="index"
        @click="$emit(item.event)"
      >
        <template #prepend>
          <v-icon :color="item.color ? item.color : undefined">
            {{ item.icon }}
          </v-icon>
        </template>
        <v-list-item-title>{{ item.title }}</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script lang="ts">
import type { ContextMenuItem } from "~/composables/use-context-presents";

export default defineNuxtComponent({
  props: {
    items: {
      type: Array as () => ContextMenuItem[],
      required: true,
    },
    menuTop: {
      type: Boolean,
      default: true,
    },
    fab: {
      type: Boolean,
      default: false,
    },
    color: {
      type: String,
      default: "grey-darken-2",
    },
  },
});
</script>
