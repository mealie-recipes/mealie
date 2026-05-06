<template>
  <div class="d-flex justify-space-between align-center mx-2">
    <div class="handle">
      <span class="mr-2">
        <v-icon :color="labelColor">
          {{ $globals.icons.tags }}
        </v-icon>
      </span>
      {{ modelValue.label.name }}
    </div>
    <div
      style="min-width: 72px"
      class="ml-auto text-right"
    >
      <v-menu
        offset-x
        start
        min-width="125px"
      >
        <template #activator="{ props: hoverProps }">
          <v-btn
            size="small"
            variant="text"
            class="ml-2 handle"
            icon
            v-bind="hoverProps"
          >
            <v-icon>
              {{ $globals.icons.arrowUpDown }}
            </v-icon>
          </v-btn>
        </template>
      </v-menu>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ShoppingListMultiPurposeLabelOut } from "~/lib/api/types/household";

const props = defineProps<{
  useColor?: boolean;
}>();
const modelValue = defineModel<ShoppingListMultiPurposeLabelOut>({ required: true });

const labelColor = ref<string | undefined>(props.useColor ? modelValue.value.label.color : undefined);
</script>
