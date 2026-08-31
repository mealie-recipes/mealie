<template>
  <v-card
    variant="outlined"
    color="info"
    class="d-flex justify-space-between align-center"
    @click="$emit('parse')"
  >
    <v-card-text>
      {{ $t('recipe.parser.try-again-with-parser', { parser: currentParserText }) }}
    </v-card-text>
    <v-card-actions>
      <BaseButton edit minor @click.stop="open = true">
        {{ $t('recipe.parser.select-parser') }}
      </BaseButton>
    </v-card-actions>
  </v-card>
  <v-alert
    v-if="showNlpLanguageHint"
    type="info"
    variant="tonal"
    density="compact"
    class="mt-3 text-body-2"
  >
    {{ $t("recipe.parser.natural-language-processor-english-only") }}
  </v-alert>
  <BaseDialog
    v-model="open"
    :title="$t('recipe.parser.select-parser')"
    :icon="$globals.icons.fileSign"
  >
    <v-list>
      <v-list-item
        v-for="(parser) in availableParsers.filter(({ hide }) => !hide)"
        :key="parser.value"
        link
        :append-icon="$globals.icons.chevronRight"
        @click="
          currentParser = parser.value as Parser;
          $emit('parse')
        "
      >
        {{ parser.text }}
      </v-list-item>
    </v-list>
  </BaseDialog>
</template>

<script setup lang="ts">
import type { MenuItem } from "~/components/global/BaseOverflowButton.vue";
import type { Parser } from "~/lib/api/user/recipes/recipe";

defineProps<{ availableParsers: MenuItem[]; showNlpLanguageHint: boolean }>();
const emit = defineEmits<{ parse: [] }>();
const currentParser = defineModel<Parser>({ default: "nlp" });

const { t } = useI18n();

const currentParserText = computed(() => {
  switch (currentParser.value) {
    case "brute": return t("recipe.parser.brute-parser");
    case "openai": return t("recipe.parser.openai-parser");
  }
  return t("recipe.parser.natural-language-processor");
});
const open = ref(false);
watch(currentParser, () => emit("parse"));
</script>
