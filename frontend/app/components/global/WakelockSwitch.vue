<template>
  <div
    v-if="wakeIsSupported"
    class="d-print-none d-flex px-2"
    :class="$vuetify.display.smAndDown ? 'justify-center' : 'justify-end'"
  >
    <v-switch
      v-model="wakeLock"
      color="primary"
      :label="$t('recipe.screen-awake')"
    />
  </div>
</template>

<script setup lang="ts">
import { useWakeLock } from "@vueuse/core";
import { useUserExperiencePreferences } from "~/composables/use-users/preferences";

const { isSupported: wakeIsSupported, isActive, request, release } = useWakeLock();
const userExperiencePreferences = useUserExperiencePreferences();

function handleLock() {
  if (userExperiencePreferences.value.lockScreen) {
    lockScreen();
  }
  else {
    unlockScreen();
  }
}

const wakeLock = computed({
  get: () => userExperiencePreferences.value.lockScreen,
  set: () => {
    userExperiencePreferences.value.lockScreen = !userExperiencePreferences.value.lockScreen;
    handleLock();
  },
});
async function lockScreen() {
  if (wakeIsSupported) {
    console.debug("Wake Lock Requested");
    await request("screen");
  }
}
async function unlockScreen() {
  if (wakeIsSupported || isActive.value) {
    console.debug("Wake Lock Released");
    await release();
  }
}
onMounted(() => handleLock());
onUnmounted(() => unlockScreen());
</script>
