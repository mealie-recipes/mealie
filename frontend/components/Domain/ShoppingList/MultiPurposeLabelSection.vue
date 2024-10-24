<template>
  <div class="d-flex justify-space-between align-center mx-2">
    <div class="handle">
      <span class="mr-2">
        <v-icon :color="labelColor">
          {{ $globals.icons.tags }}
        </v-icon>
      </span>
      {{ value.label.name }}
    </div>
    <div style="min-width: 72px" class="ml-auto text-right">
      <v-menu offset-x left min-width="125px">
        <template #activator="{ on, attrs }">
          <v-btn small class="ml-2 handle" icon v-bind="attrs" v-on="on">
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
import { defineComponent, ref } from "@nuxtjs/composition-api";
import { ShoppingListMultiPurposeLabelOut } from "~/lib/api/types/household";

export default defineComponent({
  props: {
    value: {
      type: Object as () => ShoppingListMultiPurposeLabelOut,
      required: true,
    },
    useColor: {
      type: Boolean,
      default: false,
    }
  },
  setup(props, context) {
    const labelColor = ref<string | undefined>(props.useColor ? props.value.label.color : undefined);

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
