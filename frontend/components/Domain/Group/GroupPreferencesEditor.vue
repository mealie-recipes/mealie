<template>
  <div v-if="preferences">
    <BaseCardSectionTitle :title="$tc('group.general-preferences')"></BaseCardSectionTitle>
    <v-checkbox v-model="preferences.privateGroup" class="mt-n4" :label="$t('group.private-group')"></v-checkbox>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    value: {
      type: Object,
      required: true,
    },
  },
  setup(props, context) {
    const preferences = computed({
      get() {
        return props.value;
      },
      set(val) {
        context.emit("input", val);
      },
    });

    return {
      preferences,
    };
  },
});
</script>

<style lang="scss" scoped>
</style>
