<template>
  <div>
    <v-chip v-for="(time, index) in allTimes" :key="index" label color="accent custom-transparent" class="ma-1">
      <v-icon left>
        {{ $globals.icons.clockOutline }}
      </v-icon>
      {{ time.name }} |
      {{ time.value }}
    </v-chip>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    prepTime: {
      type: String,
      default: null,
    },
    totalTime: {
      type: String,
      default: null,
    },
    performTime: {
      type: String,
      default: null,
    },
  },
  setup(props) {
    const { i18n } = useContext();

    function isEmpty(str: string | null) {
      return !str || str.length === 0;
    }

    const showCards = computed(() => {
      return [props.prepTime, props.totalTime, props.performTime].some((x) => !isEmpty(x));
    });

    const validateTotalTime = computed(() => {
      return !isEmpty(props.totalTime) ? { name: i18n.t("recipe.total-time"), value: props.totalTime } : null;
    });

    const validatePrepTime = computed(() => {
      return !isEmpty(props.prepTime) ? { name: i18n.t("recipe.prep-time"), value: props.prepTime } : null;
    });

    const validatePerformTime = computed(() => {
      return !isEmpty(props.performTime) ? { name: i18n.t("recipe.perform-time"), value: props.performTime } : null;
    });

    const allTimes = computed(() => {
      return [validateTotalTime.value, validatePrepTime.value, validatePerformTime.value].filter((x) => x !== null);
    });

    return {
      showCards,
      allTimes,
    }
  },
});
</script>

<style scoped>
.time-card-flex {
  width: fit-content;
}
.custom-transparent {
  opacity: 0.7;
}
</style>
