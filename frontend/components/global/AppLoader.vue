<template>
  <div class="mx-auto my-3 justify-center" style="display: flex;">
    <div style="display: inline;">
      <v-progress-circular :width="size.width" :size="size.size" color="primary lighten-2" indeterminate>
        <div class="text-center">
          <v-icon :size="size.icon" color="primary lighten-2">
            {{ $globals.icons.primary }}
          </v-icon>
          <div v-if="large" class="text-small">
            <slot>
              {{ (small || tiny) ? "" : waitingText }}
            </slot>
          </div>
        </div>
      </v-progress-circular>
      <div v-if="!large" class="text-small">
        <slot>
          {{ (small || tiny) ? "" : waitingTextCalculated }}
        </slot>
      </div>
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
    tiny: {
      type: Boolean,
      default: false,
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
    waitingText: {
      type: String,
      default: undefined,
    }
  },
  setup(props) {
    const size = computed(() => {
      if (props.tiny) {
        return {
          width: 2,
          icon: 0,
          size: 25,
        };
      }
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
    const waitingTextCalculated = props.waitingText == null ? i18n.t("general.loading-recipes") : props.waitingText;

    return {
      size,
      waitingTextCalculated,
    };
  },
});
</script>
