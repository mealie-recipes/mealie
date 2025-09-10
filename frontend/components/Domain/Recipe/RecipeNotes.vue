<template>
  <div
    v-if="model.length > 0 || edit"
    class="mt-8"
  >
    <h2 class="my-4 text-h5 font-weight-medium opacity-80">
      {{ $t("recipe.note") }}
    </h2>
    <div
      v-for="(note, index) in model"
      :id="'note' + index"
      :key="'note' + index"
      class="mt-1"
    >
      <v-card v-if="edit">
        <v-card-text>
          <div class="d-flex align-center">
            <v-text-field
              v-model="model[index]['title']"
              variant="underlined"
              :label="$t('recipe.title')"
            />
            <v-btn
              icon
              class="mr-2"
              elevation="0"
              @click="removeByIndex(index)"
            >
              <v-icon>{{ $globals.icons.delete }}</v-icon>
            </v-btn>
          </div>
          <v-textarea
            v-model="model[index]['text']"
            variant="underlined"
            auto-grow
            :placeholder="$t('recipe.note')"
          />
        </v-card-text>
      </v-card>
      <div v-else>
        <v-card-title class="text-subtitle-1 font-weight-medium py-1">
          {{ note.title }}
        </v-card-title>
        <v-card-text>
          <SafeMarkdown :source="note.text" />
        </v-card-text>
      </div>
    </div>

    <div
      v-if="edit"
      class="d-flex justify-end"
    >
      <BaseButton
        class="ml-auto my-2"
        @click="addNote"
      >
        {{ $t("general.add") }}
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { RecipeNote } from "~/lib/api/types/recipe";

const model = defineModel<RecipeNote[]>({ default: () => [] });

defineProps({
  edit: {
    type: Boolean,
    default: true,
  },
});

function addNote() {
  model.value = [...model.value, { title: "", text: "" }];
}

function removeByIndex(index: number) {
  const newNotes = [...model.value];
  newNotes.splice(index, 1);
  model.value = newNotes;
}
</script>
