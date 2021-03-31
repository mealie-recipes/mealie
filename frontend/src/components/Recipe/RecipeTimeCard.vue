<template>
  <v-card
    color="accent"
    class="custom-transparent d-flex justify-start align-center text-center "
    tile
    :width="`${timeCardWidth}`"
    height="55"
    v-if="totalTime || prepTime || performTime"
  >
    <v-card flat color="rgb(255, 0, 0, 0.0)">
      <v-icon large color="white" class="mx-2"> mdi-clock-outline </v-icon>
    </v-card>

    <v-divider vertical color="white" class="py-1" v-if="totalTime">
    </v-divider>
    <v-card flat color="rgb(255, 0, 0, 0.0)" class=" my-2 " v-if="totalTime">
      <v-card-text class="white--text">
        <div>
          <strong> {{ $t("recipe.total-time") }} </strong>
        </div>
        <div>{{ totalTime }}</div>
      </v-card-text>
    </v-card>

    <v-divider vertical color="white" class="py-1" v-if="prepTime"> </v-divider>

    <v-card
      flat
      color="rgb(255, 0, 0, 0.0)"
      class="white--text my-2 "
      v-if="prepTime"
    >
      <v-card-text class="white--text">
        <div>
          <strong> {{ $t("recipe.prep-time") }} </strong>
        </div>
        <div>{{ prepTime }}</div>
      </v-card-text>
    </v-card>

    <v-divider vertical color="white" class="my-1" v-if="performTime">
    </v-divider>

    <v-card
      flat
      color="rgb(255, 0, 0, 0.0)"
      class="white--text py-2 "
      v-if="performTime"
    >
      <v-card-text class="white--text">
        <div>
          <strong> {{ $t("recipe.perform-time") }} </strong>
        </div>
        <div>{{ performTime }}</div>
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
    timeLength() {
      let times = [];
      let timeArray = [this.totalTime, this.prepTime, this.performTime];
      timeArray.forEach(element => {
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
      let width = 80;
      timeArray.forEach(element => {
        if (element) {
          width += 95;
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

<style scoped>
.custom-transparent {
  opacity: 0.7;
}
</style>