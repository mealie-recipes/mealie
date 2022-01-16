<template>
  <v-text-field v-model="inputVal" label="Color">
    <template #prepend>
      <v-btn class="elevation-0" small height="30px" width="30px" :color="inputVal || 'grey'" @click="setRandomHex">
        <v-icon color="white">
          {{ $globals.icons.refreshCircle }}
        </v-icon>
      </v-btn>
    </template>
    <template #append>
      <v-menu v-model="menu" left nudge-left="30" nudge-top="20" :close-on-content-click="false">
        <template #activator="{ on }">
          <v-icon v-on="on">
            {{ $globals.icons.formatColorFill }}
          </v-icon>
        </template>
        <v-card>
          <v-card-text class="pa-0">
            <v-color-picker v-model="inputVal" flat hide-inputs show-swatches swatches-max-height="200" />
          </v-card-text>
        </v-card>
      </v-menu>
    </template>
  </v-text-field>
</template>

<script lang="ts">
import { defineComponent, computed, ref } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    value: {
      type: String,
      required: true,
    },
  },
  setup(props, context) {
    const menu = ref(false);

    const inputVal = computed({
      get: () => {
        return props.value;
      },
      set: (val) => {
        context.emit("input", val);
      },
    });

    function getRandomHex() {
      return "#000000".replace(/0/g, function () {
        return (~~(Math.random() * 16)).toString(16);
      });
    }

    function setRandomHex() {
      inputVal.value = getRandomHex();
    }

    return {
      menu,
      setRandomHex,
      inputVal,
    };
  },
});
</script>