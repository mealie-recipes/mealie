<template>
  <v-text-field
    v-model="modelValue"
    :label="$t('general.color')"
  >
    <template #prepend>
      <v-btn
        class="elevation-0"
        size="small"
        height="30px"
        width="30px"
        :color="modelValue || 'grey'"
        @click="setRandomHex"
      >
        <v-icon color="white">
          {{ $globals.icons.refreshCircle }}
        </v-icon>
      </v-btn>
    </template>
    <template #append>
      <v-menu
        v-model="menu"
        start
        nudge-left="30"
        nudge-top="20"
        :close-on-content-click="false"
      >
        <template #activator="{ props }">
          <v-icon v-bind="props">
            {{ $globals.icons.formatColorFill }}
          </v-icon>
        </template>
        <v-card>
          <v-card-text class="pa-0">
            <v-color-picker
              v-model="modelValue"
              flat
              hide-inputs
              show-swatches
              swatches-max-height="200"
            />
          </v-card-text>
        </v-card>
      </v-menu>
    </template>
  </v-text-field>
</template>

<script setup lang="ts">
const modelValue = defineModel({
  type: String,
  required: true,
});

const menu = ref(false);

function getRandomHex() {
  return "#000000".replace(/0/g, function () {
    return (~~(Math.random() * 16)).toString(16);
  });
}

function setRandomHex() {
  modelValue.value = getRandomHex();
}
</script>
