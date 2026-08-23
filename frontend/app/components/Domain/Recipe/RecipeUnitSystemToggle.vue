<template>
  <v-menu
    v-model="menu"
    offset-y
    top
    nudge-top="6"
    :close-on-content-click="false"
  >
    <template #activator="{ props: activatorProps }">
      <v-tooltip
        size="small"
        location="top"
        color="secondary-darken-1"
      >
        <template #activator="{ props: tooltipProps }">
          <v-card
            class="pa-1 px-2"
            dark
            color="secondary-darken-1"
            size="small"
            v-bind="{ ...activatorProps, ...tooltipProps }"
            :style="{ cursor: 'pointer' }"
          >
            <v-icon
              size="small"
              class="mr-2"
            >
              {{ $globals.icons.units }}
            </v-icon>
            <span>{{ activeLabel }}</span>
          </v-card>
        </template>
        <span>{{ $t("recipe.unit-system-tooltip") }}</span>
      </v-tooltip>
    </template>
    <v-card min-width="260px">
      <v-list density="compact">
        <v-list-subheader>{{ $t("recipe.unit-system") }}</v-list-subheader>
        <v-list-item
          v-for="option in unitSystemOptions"
          :key="option.value"
          :active="option.value === unitSystem"
          @click="unitSystem = option.value"
        >
          <v-list-item-title>{{ option.label }}</v-list-item-title>
        </v-list-item>

        <v-divider class="my-1" />

        <v-list-subheader>{{ $t("recipe.temperature-unit") }}</v-list-subheader>
        <v-list-item
          v-for="option in temperatureUnitOptions"
          :key="option.value"
          :active="option.value === temperatureUnit"
          @click="temperatureUnit = option.value"
        >
          <v-list-item-title>{{ option.label }}</v-list-item-title>
        </v-list-item>
      </v-list>
      <v-card-text
        v-if="unitSystem !== 'original'"
        class="text-caption pt-0"
      >
        {{ $t("recipe.unit-system-note") }}
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script setup lang="ts">
import { useUnitSystem } from "~/composables/recipes/use-unit-system";
import type { TemperatureUnit, UnitSystem } from "~/lib/api/types/user";

const unitSystem = defineModel<UnitSystem>("unitSystem", { required: true });
const temperatureUnit = defineModel<TemperatureUnit>("temperatureUnit", { required: true });

const { unitSystemOptions, temperatureUnitOptions } = useUnitSystem();
const menu = ref(false);

const activeLabel = computed(() =>
  unitSystemOptions.value.find(o => o.value === unitSystem.value)?.label ?? unitSystemOptions.value[0]?.label,
);
</script>
