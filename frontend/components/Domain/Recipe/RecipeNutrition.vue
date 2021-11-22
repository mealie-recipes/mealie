<template>
  <div v-if="valueNotNull || edit">
    <v-card class="mt-2">
      <v-card-title class="pt-2 pb-0">
        {{ $t("recipe.nutrition") }}
      </v-card-title>
      <v-divider class="mx-2 my-1"></v-divider>
      <v-card-text v-if="edit">
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
      </v-card-text>
      <v-list v-if="showViewer" dense class="mt-0 pt-0">
        <v-list-item v-for="(item, key, index) in labels" :key="index" style="min-height: 25px" dense>
          <v-list-item-content>
            <v-list-item-title class="pl-4 caption flex row">
              <div>{{ item.label }}</div>
              <div class="ml-auto mr-1">{{ value[key] }}</div>
              <div>{{ item.suffix }}</div>
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </div>
</template>

<script>
export default {
  props: {
    value: {
      type: Object,
      required: true,
    },
    edit: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      labels: {
        calories: {
          label: this.$t("recipe.calories"),
          suffix: this.$t("recipe.calories-suffix"),
        },
        fatContent: {
          label: this.$t("recipe.fat-content"),
          suffix: this.$t("recipe.grams"),
        },
        fiberContent: {
          label: this.$t("recipe.fiber-content"),
          suffix: this.$t("recipe.grams"),
        },
        proteinContent: {
          label: this.$t("recipe.protein-content"),
          suffix: this.$t("recipe.grams"),
        },
        sodiumContent: {
          label: this.$t("recipe.sodium-content"),
          suffix: this.$t("recipe.milligrams"),
        },
        sugarContent: {
          label: this.$t("recipe.sugar-content"),
          suffix: this.$t("recipe.grams"),
        },
        carbohydrateContent: {
          label: this.$t("recipe.carbohydrate-content"),
          suffix: this.$t("recipe.grams"),
        },
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

<style lang="scss" scoped></style>
