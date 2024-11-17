<template>
    <div
        v-if="wakeIsSupported"
        class="d-print-none d-flex px-2"
        :class="$vuetify.breakpoint.smAndDown ? 'justify-center' : 'justify-end'"
    >
        <v-switch v-model="wakeLock" small :label="$t('recipe.screen-awake')" />
    </div>
</template>

<script lang="ts">
import { defineComponent, computed, onMounted, onUnmounted } from "@nuxtjs/composition-api";
import { useWakeLock } from "@vueuse/core";

export default defineComponent({
    setup() {
        const { isSupported: wakeIsSupported, isActive, request, release } = useWakeLock();
        const wakeLock = computed({
            get: () => isActive.value,
            set: () => {
                if (isActive.value) {
                    unlockScreen();
                } else {
                    lockScreen();
                }
            },
        });
        async function lockScreen() {
            if (wakeIsSupported) {
                console.debug("Wake Lock Requested");
                await request("screen");
            }
        }
        async function unlockScreen() {
            if (wakeIsSupported || isActive) {
                console.debug("Wake Lock Released");
                await release();
            }
        }
        onMounted(() => lockScreen());
        onUnmounted(() => unlockScreen());

        return {
            wakeLock,
            wakeIsSupported,
        };
    },
});
</script>
