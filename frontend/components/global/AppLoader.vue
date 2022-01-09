<template>
  <div class="mx-auto">
    <v-progress-circular :width="size.width" :size="size.size" color="primary lighten-2" indeterminate>
      <div class="text-center">
        <v-icon :size="size.icon" color="primary lighten-2">
          {{ $globals.icons.primary }}
        </v-icon>
        <div v-if="large" class="text-small">
          <slot>
            {{ small ? "" : waitingText }}
          </slot>
        </div>
      </div>
    </v-progress-circular>
    <div v-if="!large" class="text-small">
      <slot>
        {{ small ? "" : waitingText }}
      </slot>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    loading: {
      type: Boolean,
      default: true,
    },
    small: {
      type: Boolean,
      default: false,
    },
    medium: {
      type: Boolean,
      default: true,
    },
    large: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const size = computed(() => {
      if (props.small) {
        return {
          width: 2,
          icon: 30,
          size: 50,
        };
      } else if (props.large) {
        return {
          width: 4,
          icon: 120,
          size: 200,
        };
      }
      return {
        width: 3,
        icon: 75,
        size: 125,
      };
    });

    const { i18n } = useContext();
    const waitingText = i18n.t("general.loading-recipes");

    return {
      size,
      waitingText,
    };
  },
});
</script>
