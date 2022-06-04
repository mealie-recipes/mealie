<template>
  <v-menu
    offset-y
    left
    :bottom="!menuTop"
    :nudge-bottom="!menuTop ? '5' : '0'"
    :top="menuTop"
    :nudge-top="menuTop ? '5' : '0'"
    allow-overflow
    close-delay="125"
    open-on-hover
    content-class="d-print-none"
  >
    <template #activator="{ on, attrs }">
      <v-btn :fab="fab" :small="fab" :color="color" :icon="!fab" dark v-bind="attrs" v-on="on" @click.prevent>
        <v-icon>{{ $globals.icons.dotsVertical }}</v-icon>
      </v-btn>
    </template>
    <v-list dense>
      <v-list-item v-for="(item, index) in items" :key="index" @click="$emit(item.event)">
        <v-list-item-icon>
          <v-icon :color="item.color ? item.color : undefined">
            {{ item.icon }}
          </v-icon>
        </v-list-item-icon>
        <v-list-item-title>{{ item.title }}</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { ContextMenuItem } from "~/composables/use-context-presents";

export default defineComponent({
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
      default: "grey darken-2",
    },
  },
});
</script>
