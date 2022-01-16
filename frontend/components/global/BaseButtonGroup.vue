<template>
  <v-item-group>
    <template v-for="btn in buttons">
      <v-menu v-if="btn.children" :key="'menu-' + btn.event" active-class="pa-0" offset-x left>
        <template #activator="{ on, attrs }">
          <v-btn tile large icon v-bind="attrs" v-on="on">
            <v-icon>
              {{ btn.icon }}
            </v-icon>
          </v-btn>
        </template>
        <v-list dense>
          <v-list-item v-for="(child, idx) in btn.children" :key="idx" dense @click="$emit(child.event)">
            <v-list-item-title>{{ child.text }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
      <v-tooltip
        v-else
        :key="'btn-' + btn.event"
        open-delay="200"
        transition="slide-y-reverse-transition"
        dense
        bottom
        content-class="text-caption"
      >
        <template #activator="{ on, attrs }">
          <v-btn tile large icon v-bind="attrs" @click="$emit(btn.event)" v-on="on">
            <v-icon> {{ btn.icon }} </v-icon>
          </v-btn>
        </template>
        <span>{{ btn.text }}</span>
      </v-tooltip>
    </template>
  </v-item-group>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";

export interface ButtonOption {
  icon: string;
  text: string;
  event: string;
  children?: ButtonOption[];
}

export default defineComponent({
  props: {
    buttons: {
      type: Array as () => ButtonOption[],
      required: true,
    },
  },
});
</script>
