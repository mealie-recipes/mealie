<template>
  <v-card
    color="accent"
    class="custom-transparent d-flex justify-start align-center text-center time-card-flex"
    tile
    v-if="showCards"
  >
    <v-card flat color="rgb(255, 0, 0, 0.0)">
      <v-icon large color="white" class="mx-2"> mdi-clock-outline </v-icon>
    </v-card>

    <v-card
      v-for="(time, index) in allTimes"
      :key="index"
      class="d-flex justify-start align-center text-center time-card-flex"
      flat
      color="rgb(255, 0, 0, 0.0)"
    >
      <v-card-text class="caption white--text py-2">
        <div>
          <strong> {{ time.name }} </strong>
        </div>
        <div>{{ time.value }}</div>
      </v-card-text>
    </v-card>
  </v-card>
</template>

<script>
export default {
  props: {
    prepTime: String,
    totalTime: String,
    performTime: String,
  },
  computed: {
    showCards() {
      return [this.prepTime, this.totalTime, this.performTime].some(
        x => !this.isEmpty(x)
      );
    },
    allTimes() {
      return [
        this.validateTotalTime,
        this.validatePrepTime,
        this.validatePerformTime,
      ].filter(x => x !== null);
    },
    validateTotalTime() {
      return !this.isEmpty(this.totalTime)
        ? { name: this.$t("recipe.total-time"), value: this.totalTime }
        : null;
    },
    validatePrepTime() {
      return !this.isEmpty(this.prepTime)
        ? { name: this.$t("recipe.prep-time"), value: this.prepTime }
        : null;
    },
    validatePerformTime() {
      return !this.isEmpty(this.performTime)
        ? { name: this.$t("recipe.perform-time"), value: this.performTime }
        : null;
    },
  },
  methods: {
    isEmpty(str) {
      return !str || str.length === 0;
    },
  },
};
</script>

<style scoped>
.time-card-flex {
  width: fit-content;
}
.custom-transparent {
  opacity: 0.7;
}
</style>