<template>
  <div class="text-center">
    <v-menu
      top
      offset-y
      :right="right"
      :left="!right"
      open-on-hover
    >
      <template #activator="{ props }">
        <v-btn
          :size="small ? 'small' : undefined"
          icon
          v-bind="props"
          variant="flat"
          @click.stop
        >
          <v-icon :small="small">
            {{ $globals.icons.help }}
          </v-icon>
        </v-btn>
      </template>
      <v-card max-width="300px">
        <v-card-text>
          <slot />
        </v-card-text>
      </v-card>
    </v-menu>
  </div>
</template>

<script lang="ts">
export default defineNuxtComponent({
  props: {
    small: {
      type: Boolean,
      default: false,
    },
    right: {
      type: Boolean,
      default: false,
    },
  },
});
</script>

<style scoped></style>
