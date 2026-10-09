<template>
  <v-menu active-class="pa-0" offset-y top>
    <template #activator="{ props: hoverProps }">
      <v-btn icon color="secondary" v-bind="hoverProps" class="ml-auto">
        <v-icon>
          {{ $globals.icons.dotsHorizontal }}
        </v-icon>
      </v-btn>
    </template>
    <v-list density="compact">
      <template
        v-for="(child, idx) in [
          {
            text: $t('meal-plan.remove-from-plan'),
            icon: $globals.icons.calendarRemove,
            event: 'mealplan-remove',
          },
          {
            text: $t('meal-plan.edit-meal-plan'),
            icon: $globals.icons.calendarEdit,
            event: 'mealplan-edit',
          },
        ]"
        :key="idx"
      >
        <v-list-item
          density="compact"
          :prepend-icon="child.icon"
          @click="$emit(child.event as any)"
        >
          <v-list-item-title>{{ child.text }}</v-list-item-title>
        </v-list-item>
      </template>
    </v-list>
  </v-menu>
</template>

<script setup lang="ts">
defineEmits<{
  "mealplan-remove": [];
  "mealplan-edit": [];
}>();
</script>
