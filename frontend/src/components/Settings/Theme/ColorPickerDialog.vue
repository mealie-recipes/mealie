<template>
  <div>
    <!-- <v-btn block :color="value" @click="dialog = true">
      {{ buttonText }}
    </v-btn>
    <v-dialog v-model="dialog" width="400">
      <v-card>
        <v-card-title> {{ buttonText }} {{$t('settings.color')}} </v-card-title>
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
          <v-btn text @click="toggleSwatches"> {{$t('settings.swatches')}} </v-btn>
          <v-btn text @click="dialog = false"> {{$t('general.select')}} </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog> -->

    <v-text-field
      v-model="value"
      v-mask="mask"
      hide-details
      class="ma-0 pa-0"
      solo
    >
      <template v-slot:append>
        <v-menu
          v-model="menu"
          top
          nudge-bottom="105"
          nudge-left="16"
          :close-on-content-click="false"
        >
          <template v-slot:activator="{ on }">
            <div :style="swatchStyle" v-on="on" swatches-max-height="300" />
          </template>
          <v-card>
            <v-card-text class="pa-0">
              <v-color-picker v-model="value" flat show-swatches />
            </v-card-text>
          </v-card>
        </v-menu>
      </template>
    </v-text-field>
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
      color: "#1976D2FF",
      mask: "!#XXXXXXXX",
      menu: false,
    };
  },
  computed: {
    swatchStyle() {
      const { value, menu } = this;
      return {
        backgroundColor: value,
        cursor: "pointer",
        height: "30px",
        width: "30px",
        borderRadius: menu ? "50%" : "4px",
        transition: "border-radius 200ms ease-in-out",
      };
    },
  },
  watch: {
    color() {
      this.updateColor();
    },
  },
  methods: {
    updateColor() {
      this.$emit("input", this.color);
    },
  },
};
</script>

<style>
</style>