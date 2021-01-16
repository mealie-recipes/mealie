<template>
  <v-card color="accent" class="transparent" tile :width="`${timeCardWidth}`">
    <v-card-text
      class="text-caption white--text"
      v-if="totalTime || prepTime || performTime"
    >
      <v-row align="center" dense>
        <v-col :cols="iconColumn">
          <v-icon large color="white"> mdi-clock-outline </v-icon>
        </v-col>
        <v-divider
          vertical
          color="white"
          class="my-1"
          v-if="totalTime"
        ></v-divider>
        <v-col v-if="totalTime">
          <div><strong> Total Time </strong></div>
          <div>{{ totalTime }}</div>
        </v-col>
        <v-divider
          vertical
          color="white"
          class="my-1"
          v-if="prepTime"
        ></v-divider>
        <v-col v-if="prepTime">
          <div><strong> Prep Time </strong></div>
          <div>{{ prepTime }}</div>
        </v-col>
        <v-divider
          vertical
          color="white"
          class="my-1"
          v-if="performTime"
        ></v-divider>
        <v-col v-if="performTime">
          <div><strong> Cook Time </strong></div>
          <div>{{ performTime }}</div>
        </v-col>
      </v-row>
    </v-card-text>
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
    timeLength() {
      let times = [];
      let timeArray = [this.totalTime, this.prepTime, this.performTime];
      timeArray.forEach((element) => {
        if (element) {
          times.push(element);
        }
      });

      return times.length;
    },
    iconColumn() {
      switch (this.timeLength) {
        case 0:
          return null;
        case 1:
          return 4;
        case 2:
          return 3;
        case 3:
          return 2;
        default:
          return 1;
      }
    },
    timeCardWidth() {
      let timeArray = [this.totalTime, this.prepTime, this.performTime];
      let width = 120;
      timeArray.forEach((element) => {
        if (element) {
          width += 70;
        }
      });

      if (this.$vuetify.breakpoint.name === "xs") {
        return "100%";
      }

      return `${width}px`;
    },
  },
};
</script>

<style>
.transparent {
  opacity: 70% !important;
}
</style>