<template>
  <div class="text-center">
    <v-snackbar v-model="toastAlert.open" top :color="toastAlert.color" timeout="2000" @input="toastAlert.open = false">
      <v-icon dark left>
        {{ icon }}
      </v-icon>

      {{ toastAlert.title }}
      {{ toastAlert.text }}

      <template #action="{ attrs }">
        <v-btn text v-bind="attrs" @click="toastAlert.open = false"> {{ $t('general.close') }} </v-btn>
      </template>
    </v-snackbar>
    <v-snackbar
      content-class="py-2"
      dense
      bottom
      right
      :value="toastLoading.open"
      :timeout="-1"
      :color="toastLoading.color"
      @input="toastLoading.open = false"
    >
      <div class="d-flex flex-column align-center justify-start" @click="toastLoading.open = false">
        <div class="mb-2 mt-0 text-subtitle-1 text-center">
          {{ toastLoading.text }}
        </div>
        <v-progress-linear indeterminate color="white darken-2"></v-progress-linear>
      </div>
    </v-snackbar>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";
import { toastAlert, toastLoading } from "~/composables/use-toast";

export default defineComponent({
  setup() {
    const icon = computed(() => {
      switch (toastAlert.color) {
        case "error":
          return "mdi-alert";
        case "success":
          return "mdi-check-bold";
        case "info":
          return "mdi-information-outline";
        default:
          return "mdi-alert";
      }
    });

    return { icon, toastAlert, toastLoading };
  },
});
</script>
