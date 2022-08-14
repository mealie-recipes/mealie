<template>
  <div class="d-flex justify-center pb-6 mt-n1">
    <div style="flex-basis: 500px">
      <strong> {{ $t("user.password-strength", { strength: pwStrength.strength.value }) }}</strong>
      <v-progress-linear
        :value="pwStrength.score.value"
        class="rounded-lg"
        :color="pwStrength.color.value"
        height="15"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, toRef } from "@nuxtjs/composition-api";
import { usePasswordStrength } from "~/composables/use-passwords";

export default defineComponent({
  props: {
    value: {
      type: String,
      default: "",
    },
  },
  setup(props) {
    const asRef = toRef(props, "value");

    const pwStrength = usePasswordStrength(asRef);

    return {
      pwStrength,
    };
  },
});
</script>

<style scoped></style>
