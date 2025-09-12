<template>
  <div class="d-flex pb-6 mt-n1 ml-10">
    <div style="flex-basis: 500px">
      <strong> {{ $t("user.password-strength", { strength: pwStrength.strength.value }) }}</strong>
      <v-progress-linear
        v-model="pwStrength.score.value"
        rounded
        :color="pwStrength.color.value"
        height="15"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePasswordStrength } from "~/composables/use-passwords";

const modelValue = defineModel<string>({ default: "" });
const i18n = useI18n();

const pwStrength = usePasswordStrength(modelValue, i18n);
</script>
