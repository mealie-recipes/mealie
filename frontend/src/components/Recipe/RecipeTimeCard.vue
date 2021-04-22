<template>
  <v-card
    color="accent"
    class="custom-transparent d-flex justify-start align-center text-center time-card-flex"
    tile
    v-if="totalTime || prepTime || performTime"
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
      <v-card-text class="white--text py-2">
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
    allTimes() {
      return [
        this.validateTotalTime,
        this.validatePrepTime,
        this.validatePerformTime,
      ];
    },
    validateTotalTime() {
      return this.prepTime
        ? { name: this.$t("recipe.prep-time"), value: this.prepTime }
        : null;
    },
    validatePrepTime() {
      return this.prepTime
        ? { name: this.$t("recipe.prep-time"), value: this.prepTime }
        : null;
    },
    validatePerformTime() {
      return this.prepTime
        ? { name: this.$t("recipe.perform-time"), value: this.performTime }
        : null;
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