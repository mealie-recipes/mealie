<template>
  <div>
    <v-btn block :color="value" @click="dialog = true">
      {{ buttonText }}
    </v-btn>
    <v-dialog v-model="dialog" width="400">
      <v-card>
        <v-card-title> {{ buttonText }} Color </v-card-title>
        <v-card-text>
          <v-text-field v-model="color"> </v-text-field>
          <v-row>
            <v-col></v-col>
            <v-col>
              <v-color-picker
                dot-size="28"
                hide-inputs
                hide-mode-switch
                mode="hexa"
                :show-swatches="swatches"
                swatches-max-height="300"
                v-model="color"
                @change="updateColor"
              ></v-color-picker>
            </v-col>
            <v-col></v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="toggleSwatches"> Swatches </v-btn>
          <v-btn text @click="dialog = false"> Select </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  props: {
    buttonText: String,
    value: String,
  },
  data() {
    return {
      dialog: false,
      swatches: false,
      color: "#FF00FF",
    };
  },

  watch: {
    color() {
      this.updateColor();
    },
  },
  methods: {
    toggleSwatches() {
      if (this.swatches) {
        this.swatches = false;
      } else this.swatches = true;
    },
    updateColor() {
      this.$emit("input", this.color);
    },
  },
};
</script>

<style>
</style>