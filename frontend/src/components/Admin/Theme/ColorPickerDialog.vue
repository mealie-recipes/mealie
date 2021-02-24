<template>
  <div>
    <div class="text-center">
      <h3>{{ buttonText }}</h3>
    </div>
    <v-text-field
      v-model="color"
      hide-details
      class="ma-0 pa-0"
      solo
      v-show="$vuetify.breakpoint.mdAndUp"
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
              <v-color-picker v-model="color" flat mode="hexa" show-swatches />
            </v-card-text>
          </v-card>
        </v-menu>
      </template>
    </v-text-field>
    <div class="text-center" v-show="$vuetify.breakpoint.smAndDown">
      <v-menu
        v-model="menu"
        top
        nudge-bottom="105"
        nudge-left="16"
        :close-on-content-click="false"
      >
        <template v-slot:activator="{ on, attrs }">
          <v-chip label :color="`${color}`" dark v-bind="attrs" v-on="on">
            {{ color }}
          </v-chip>
        </template>
      </v-menu>
    </div>
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

<style>
</style>