<template>
  <div>
    <h2 class="my-4">Nutrition</h2>
    <div v-for="(item, key, index) in nutrition" :key="index">
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
</template>

<script>
export default {
  props: {
    value: {},
  },
  data() {
    return {
      nutrition: {
        calories: null,
        fatContent: null,
        fiberContent: null,
        proteinContent: null,
        sodiumContent: null,
        sugarContent: null,
      },
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

  methods: {
    updateValue(key, value) {
      this.$emit("input", { ...this.value, [key]: value });
    },
  },
};
</script>

<style lang="scss" scoped>
</style>