<template>
  <v-expansion-panels v-model="open">
    <slot />
  </v-expansion-panels>
</template>

<script setup lang="ts">
interface Props {
  startOpen?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  startOpen: false,
});

const open = ref(props.startOpen ? [0] : []);
</script>
