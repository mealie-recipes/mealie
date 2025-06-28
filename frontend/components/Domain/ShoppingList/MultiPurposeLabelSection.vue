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
        <template #activator="{ props }">
          <v-btn
            size="small"
            class="ml-2 handle"
            icon
            v-bind="props"
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

<script lang="ts">
import type { ShoppingListMultiPurposeLabelOut } from "~/lib/api/types/household";

export default defineNuxtComponent({
  props: {
    modelValue: {
      type: Object as () => ShoppingListMultiPurposeLabelOut,
      required: true,
    },
    useColor: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, context) {
    const labelColor = ref<string | undefined>(props.useColor ? props.modelValue.label.color : undefined);

    function contextHandler(event: string) {
      context.emit(event);
    }

    return {
      contextHandler,
      labelColor,
    };
  },
});
</script>
