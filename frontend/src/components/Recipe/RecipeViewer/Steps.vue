<template>
  <div>
    <h2 class="mb-4">{{ $t("recipe.instructions") }}</h2>
    <v-hover
      v-for="(step, index) in steps"
      :key="generateKey('step', index)"
      v-slot="{ hover }"
    >
      <v-card
        class="ma-1"
        :class="[{ 'on-hover': hover }, isDisabled(index)]"
        :elevation="hover ? 12 : 2"
        @click="toggleDisabled(index)"
      >
        <v-card-title>{{
          $t("recipe.step-index", { step: index + 1 })
        }}</v-card-title>
        <v-card-text>
          <vue-markdown :source="step.text"> </vue-markdown>
        </v-card-text>
      </v-card>
    </v-hover>
  </div>
</template>

<script>
import VueMarkdown from "@adapttive/vue-markdown";
import utils from "@/utils";
export default {
  props: {
    steps: Array,
  },
  components: {
    VueMarkdown,
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
    generateKey(item, index) {
      return utils.generateUniqueKey(item, index);
    },
  },
};
</script>

<style>
</style>