<template>
  <div class="text-center">
    <v-menu top offset-y left open-on-hover>
      <template #activator="{ on, attrs }">
        <v-btn icon v-bind="attrs" v-on="on" @click.stop>
          <v-icon> {{ $globals.icons.help }} </v-icon>
        </v-btn>
      </template>
      <v-card max-width="300px">
        <v-card-text>
          <slot></slot>
        </v-card-text>
      </v-card>
    </v-menu>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
  setup() {
    return {};
  },
});
</script>

<style scoped></style>
