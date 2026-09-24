<template v-if="_showCards">
  <div class="text-center">
    <!-- Total Time -->
    <div
      v-if="validateTotalTime"
      class="time-card-flex mx-auto"
    >
      <v-row
        no-gutters
        class="d-flex flex-no-wrap align-center"
        :style="fontSize"
      >
        <v-icon
          :x-large="!small"
          start
          color="primary"
        >
          {{ $globals.icons.clockOutline }}
        </v-icon>
        <p class="my-0">
          <span class="font-weight-bold opacity-80">{{ validateTotalTime.name }}</span><br>{{ validateTotalTime.value }}
        </p>
      </v-row>
    </div>
    <v-divider
      v-if="validateTotalTime && (validatePrepTime || validatePerformTime)"
      class="my-2"
    />
    <!-- Prep Time & Perform Time -->
    <div
      v-if="validatePrepTime || validatePerformTime"
      class="time-card-flex mx-auto"
    >
      <v-row
        no-gutters
        class="d-flex justify-center align-center"
        :class="{ 'flex-column': $vuetify.display.smAndDown }"
        style="width: 100%;"
        :style="fontSize"
      >
        <div
          v-if="validatePrepTime"
          class="d-flex flex-no-wrap my-1 align-center"
        >
          <v-icon
            :size="small ? 'small' : 'large'"
            start
            color="primary"
          >
            {{ $globals.icons.knife }}
          </v-icon>
          <p class="my-0">
            <span class="font-weight-bold opacity-80">{{ validatePrepTime.name }}</span><br>{{ validatePrepTime.value }}
          </p>
        </div>
        <v-divider
          v-if="validatePrepTime && validatePerformTime"
          vertical
          class="mx-4"
        />
        <div
          v-if="validatePerformTime"
          class="d-flex flex-no-wrap my-1 align-center"
        >
          <v-icon
            :size="small ? 'small' : 'large'"
            start
            color="primary"
          >
            {{ $globals.icons.potSteam }}
          </v-icon>
          <p class="my-0">
            <span class="font-weight-bold opacity-80">{{ validatePerformTime.name }}</span><br>{{ validatePerformTime.value }}
          </p>
        </div>
      </v-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRecipeTime } from "~/composables/recipes";

interface Props {
  prepTime?: string | null;
  totalTime?: string | null;
  performTime?: string | null;
  prepTimeSeconds?: number | null;
  totalTimeSeconds?: number | null;
  performTimeSeconds?: number | null;
  color?: string;
  small?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  prepTime: null,
  totalTime: null,
  performTime: null,
  prepTimeSeconds: null,
  totalTimeSeconds: null,
  performTimeSeconds: null,
  color: "accent custom-transparent",
  small: false,
});

const i18n = useI18n();
const { recipeTimeDisplay } = useRecipeTime();

const totalTime = computed(() => recipeTimeDisplay(props.totalTimeSeconds, props.totalTime));
const prepTime = computed(() => recipeTimeDisplay(props.prepTimeSeconds, props.prepTime));
const performTime = computed(() => recipeTimeDisplay(props.performTimeSeconds, props.performTime));

const _showCards = computed(() => {
  return [prepTime.value, totalTime.value, performTime.value].some(x => !!x);
});

const validateTotalTime = computed(() => {
  return totalTime.value ? { name: i18n.t("recipe.total-time"), value: totalTime.value } : null;
});

const validatePrepTime = computed(() => {
  return prepTime.value ? { name: i18n.t("recipe.prep-time"), value: prepTime.value } : null;
});

const validatePerformTime = computed(() => {
  return performTime.value ? { name: i18n.t("recipe.perform-time"), value: performTime.value } : null;
});

const fontSize = computed(() => {
  return props.small ? { fontSize: "smaller" } : { fontSize: "larger" };
});
</script>

<style scoped>
.text-center {
  font-size: smaller;
}
.time-card-flex {
  width: fit-content;
}
.custom-transparent {
  opacity: 0.7;
}
</style>
