<template>
  <div>
    <v-btn
      variant="outlined"
      class="rounded-xl my-1 mx-1"
      :to="to"
    >
      <v-icon
        v-if="icon != ''"
        start
      >
        {{ icon }}
      </v-icon>
      {{ text }}
    </v-btn>
  </div>
</template>

<script setup lang="ts">
defineProps({
  to: {
    type: String,
    required: true,
  },
  text: {
    type: String,
    required: true,
  },
  icon: {
    type: String,
    default: "",
  },
});
</script>
