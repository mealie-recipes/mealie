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
        size="small"
        :icon="$globals.icons.dotsVertical"
        variant="text"
        dark
        v-bind="props"
        @click.prevent
      />
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

<script setup lang="ts">
import type { ContextMenuItem } from "~/composables/use-context-presents";

defineProps({
  items: {
    type: Array as () => ContextMenuItem[],
    required: true,
  },
  menuTop: {
    type: Boolean,
    default: true,
  },
});
</script>
