<template>
  <div class="mx-auto">
    <v-progress-circular :width="size.width" :size="size.size" color="primary lighten-2" indeterminate>
      <div class="text-center">
        <v-icon :size="size.icon" color="primary lighten-2">
          {{ $globals.icons.primary }}
        </v-icon>
        <div v-if="large" class="text-small">
          <slot>
            {{ small ? "" : "Loading Recipes" }}
          </slot>
        </div>
      </div>
    </v-progress-circular>
    <div v-if="!large" class="text-small">
      <slot>
        {{ small ? "" : "Loading Recipes" }}
      </slot>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    loading: {
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
  computed: {
    size() {
      if (this.small) {
        return {
          width: 2,
          icon: 30,
          size: 50,
        };
      } else if (this.large) {
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
    },
  },
};
</script>
