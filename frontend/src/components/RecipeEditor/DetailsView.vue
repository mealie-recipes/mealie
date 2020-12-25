<template>
  <v-card-text>
    <v-row>
      <v-col cols="4">
        <h2 class="mb-4">Ingredients</h2>
        <div v-for="ingredient in ingredients" :key="ingredient">
          <v-row align="center">
            <v-checkbox hide-details class="shrink mr-2 mt-0"></v-checkbox>
            <v-text-field :value="ingredient"></v-text-field>
          </v-row>
        </div>
        <v-btn
          class="ml-n5"
          color="primary"
          fab`
          dark
          small
          @click="addIngredient"
        >
          <v-icon>mdi-plus</v-icon>
        </v-btn>

        <h2 class="mt-6">Categories</h2>
        <v-combobox
          dense
          multiple
          chips
          item-color="primary"
          deletable-chips
          :value="categories"
        >
          <template v-slot:selection="data">
            <v-chip :selected="data.selected" close color="primary" dark>
              {{ data.item }}
            </v-chip>
          </template>
        </v-combobox>

        <h2 class="mt-4">Tags</h2>
        <v-combobox dense multiple chips deletable-chips :value="tags">
          <template v-slot:selection="data">
            <v-chip :selected="data.selected" close color="primary" dark>
              {{ data.item }}
            </v-chip>
          </template>
        </v-combobox>
      </v-col>

      <v-divider :vertical="true"></v-divider>

      <v-col>
        <h2 class="mb-4">Instructions</h2>
        <div v-for="(step, index) in instructions" :key="step.text">
          <v-hover v-slot="{ hover }">
            <v-card
              class="ma-1"
              :class="[{ 'on-hover': hover }]"
              :elevation="hover ? 12 : 2"
            >
              <v-card-title>Step: {{ index + 1 }}</v-card-title>
              <v-card-text>
                <v-textarea dense :value="step.text"></v-textarea>
              </v-card-text>
            </v-card>
          </v-hover>
        </div>
        <v-btn color="primary" fab dark small @click="addStep">
          <v-icon>mdi-plus</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </v-card-text>
</template>

<script>
export default {
  props: {
    form: Boolean,
    ingredients: Array,
    instructions: Array,
    categories: Array,
    tags: Array,
  },
  data() {
    return {
      disabledSteps: [],
    };
  },

  methods: {
    toggleDisabled(stepIndex) {
      if (this.disabledSteps.includes(stepIndex)) {
        let index = this.disabledSteps.indexOf(stepIndex);
        if (index !== -1) {
          this.disabledSteps.splice(index, 1);
        }
      } else {
        this.disabledSteps.push(stepIndex);
      }
    },
    isDisabled(stepIndex) {
      if (this.disabledSteps.includes(stepIndex)) {
        return "disabled-card";
      } else {
        return;
      }
    },
    saveRecipe() {
      this.$emit("save");
    },
    deleteRecipe() {
      this.$emit("delete");
    },
    addIngredient() {
      this.$emit("addingredient");
    },
    addStep() {
      this.$emit("addstep");
    },
  },
};
</script>

<style>
.disabled-card {
  opacity: 50%;
}
</style>