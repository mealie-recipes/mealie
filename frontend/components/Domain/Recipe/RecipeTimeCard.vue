<template v-if="showCards">
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
            left
            color="primary"
          >
            {{ $globals.icons.knfife }}
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
            left
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

<script lang="ts">
export default defineNuxtComponent({
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
    color: {
      type: String,
      default: "accent custom-transparent",
    },
    small: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const i18n = useI18n();

    function isEmpty(str: string | null) {
      return !str || str.length === 0;
    }

    const showCards = computed(() => {
      return [props.prepTime, props.totalTime, props.performTime].some(x => !isEmpty(x));
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

    const fontSize = computed(() => {
      return props.small ? { fontSize: "smaller" } : { fontSize: "larger" };
    });

    return {
      showCards,
      validateTotalTime,
      validatePrepTime,
      validatePerformTime,
      fontSize,
    };
  },
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
