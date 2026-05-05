<template>
  <div>
    <v-menu
      v-model="menu"
      offset-y
      top
      nudge-top="6"
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
      <v-card min-width="220px">
        <v-list density="compact">
          <v-list-item
            v-for="option in options"
            :key="option.value"
            :active="option.value === unitSystem"
            @click="onSelect(option.value)"
          >
            <v-list-item-title>{{ option.label }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<script setup lang="ts">
import type { UnitSystem } from "~/lib/api/types/user";

const unitSystem = defineModel<UnitSystem>({ required: true });

const menu = ref<boolean>(false);
const i18n = useI18n();

const options = computed<{ label: string; value: UnitSystem }[]>(() => [
  { label: i18n.t("recipe.unit-system-original") as string, value: "original" },
  { label: i18n.t("recipe.unit-system-metric") as string, value: "metric" },
  { label: i18n.t("recipe.unit-system-imperial") as string, value: "imperial" },
  { label: i18n.t("recipe.unit-system-us") as string, value: "us" },
]);

const activeLabel = computed(() => {
  return options.value.find(o => o.value === unitSystem.value)?.label
    ?? i18n.t("recipe.unit-system-original");
});

function onSelect(value: UnitSystem) {
  unitSystem.value = value;
  menu.value = false;
}
</script>
