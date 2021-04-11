<template>
  <div v-if="valueNotNull || edit">
    <h2 class="my-4">Nutrition</h2>
    <div v-if="edit">
      <div v-for="(item, key, index) in value" :key="index">
        <v-text-field
          dense
          :value="value[key]"
          :label="labels[key].label"
          :suffix="labels[key].suffix"
          type="number"
          autocomplete="off"
          @input="updateValue(key, $event)"
        ></v-text-field>
      </div>
    </div>
    <div v-if="showViewer">
      <v-list dense>
        <v-list-item-group color="primary">
          <v-list-item v-for="(item, key, index) in labels" :key="index">
            <v-list-item-content>
              <v-list-item-title class="pl-4 text-subtitle-1 flex row ">
                <div>{{ item.label }}</div>
                <div class="ml-auto mr-1">{{ value[key] }}</div>
                <div>{{ item.suffix }}</div>
              </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    value: {},
    edit: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      labels: {
        calories: {
          label: "Calories",
          suffix: "calories",
        },
        fatContent: { label: "Fat Content", suffix: "grams" },
        fiberContent: { label: "Fiber Content", suffix: "grams" },
        proteinContent: { label: "Protein Content", suffix: "grams" },
        sodiumContent: { label: "Sodium Content", suffix: "milligrams" },
        sugarContent: { label: "Sugar Content", suffix: "grams" },
      },
    };
  },
  computed: {
    showViewer() {
      return !this.edit && this.valueNotNull;
    },
    valueNotNull() {
      for (const property in this.value) {
        const valueProperty = this.value[property];
        if (valueProperty && valueProperty !== "") return true;
      }
      return false;
    },
  },

  methods: {
    updateValue(key, value) {
      this.$emit("input", { ...this.value, [key]: value });
    },
  },
};
</script>

<style lang="scss" scoped>
</style>