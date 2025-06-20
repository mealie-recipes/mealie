<template>
  <div v-if="preferences">
    <BaseCardSectionTitle :title="$t('group.general-preferences')" />
    <v-checkbox
      v-model="preferences.privateGroup"
      class="mt-n4"
      :label="$t('group.private-group')"
    />
  </div>
</template>

<script lang="ts">
export default defineNuxtComponent({
  props: {
    modelValue: {
      type: Object,
      required: true,
    },
  },
  emits: ["update:modelValue"],
  setup(props, context) {
    const preferences = computed({
      get() {
        return props.modelValue;
      },
      set(val) {
        context.emit("update:modelValue", val);
      },
    });

    return {
      preferences,
    };
  },
});
</script>

<style lang="scss" scoped></style>
