<template>
  <div>
    <div class="text-center">
      <h3>{{ buttonText }}</h3>
    </div>
    <v-text-field v-model="color" hide-details class="ma-0 pa-0" solo>
      <template #append>
        <v-menu v-model="menu" top nudge-bottom="105" nudge-left="16" :close-on-content-click="false">
          <template #activator="{ on }">
            <div :style="swatchStyle" swatches-max-height="300" v-on="on" />
          </template>
          <v-card>
            <v-card-text class="pa-0">
              <v-color-picker v-model="color" flat mode="hexa" show-swatches />
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
    buttonText: {
      type: String,
      default: "Choose a color",
    },
    value: {
      type: String,
      default: "#ff0000",
    },
  },
  data() {
    return {
      dialog: false,
      swatches: false,
      color: this.value || "#1976D2",
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

<style></style>
