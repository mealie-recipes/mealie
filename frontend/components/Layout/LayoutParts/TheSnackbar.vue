<template>
  <div class="text-center">
    <v-snackbar
      v-model="toastAlert.open"
      location="top"
      :color="toastAlert.color"
      timeout="2000"
    >
      <v-icon
        v-if="icon"
        dark
        start
        :icon="icon"
      />

      {{ toastAlert.title }}
      {{ toastAlert.text }}

      <template #actions>
        <v-btn
          variant="text"
          @click="toastAlert.open = false"
        >
          {{ $t('general.close') }}
        </v-btn>
      </template>
    </v-snackbar>
    <v-snackbar
      v-model="toastLoading.open"
      content-class="py-2"
      density="compact"
      location="bottom"
      :timeout="-1"
      :color="toastLoading.color"
    >
      <div
        class="d-flex flex-column align-center justify-start"
        @click="toastLoading.open = false"
      >
        <div class="mb-2 mt-0 text-subtitle-1 text-center">
          {{ toastLoading.text }}
        </div>
        <v-progress-linear
          indeterminate
          color="white-darken-2"
        />
      </div>
    </v-snackbar>
  </div>
</template>

<script lang="ts">
import { useNuxtApp } from "#app";
import { toastAlert, toastLoading } from "~/composables/use-toast";

export default {
  setup() {
    const { $globals } = useNuxtApp();
    const icon = computed(() => {
      switch (toastAlert.color) {
        case "error":
          return $globals.icons.alertOutline;
        case "success":
          return $globals.icons.checkBold;
        case "info":
          return $globals.icons.informationOutline;
        default:
          return $globals.icons.alertOutline;
      }
    });

    return { icon, toastAlert, toastLoading };
  },
};
</script>
