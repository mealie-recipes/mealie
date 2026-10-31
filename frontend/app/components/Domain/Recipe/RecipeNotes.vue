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
      :key="note.referenceId || index"
      class="mt-1"
      :data-note-id="note.referenceId"
      @keydown="handleNoteKeydown($event, index)"
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
import { nextTick, onMounted, watch } from "vue";
import { uuid4 } from "~/composables/use-utils";
import type { RecipeNote } from "~/lib/api/types/recipe";

const model = defineModel<RecipeNote[]>({ default: () => [] });

const props = defineProps({
  edit: {
    type: Boolean,
    default: true,
  },
});

function handleNoteKeydown(e: KeyboardEvent, index: number) {
  if (!props.edit || e.isComposing) {
    return;
  }
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    e.stopPropagation();
    insertNote(index + 1, true);
  }
  else if ((e.ctrlKey || e.metaKey) && e.key === "Delete") {
    e.preventDefault();
    e.stopPropagation();
    removeByIndex(index);
  }
  else if ((e.ctrlKey || e.metaKey) && (e.key === "ArrowUp" || e.key === "Up")) {
    e.preventDefault();
    e.stopPropagation();
    moveNote(index, -1);
  }
  else if ((e.ctrlKey || e.metaKey) && (e.key === "ArrowDown" || e.key === "Down")) {
    e.preventDefault();
    e.stopPropagation();
    moveNote(index, 1);
  }
}

async function insertNote(dest: number, focus = false) {
  const newId = uuid4();
  model.value.splice(dest, 0, { title: "", text: "", referenceId: newId });

  if (focus) {
    await nextTick();
    const rootEl = document.querySelector(`[data-note-id="${newId}"]`);
    if (rootEl) {
      const input = (rootEl.querySelector("input") || rootEl.querySelector("textarea")) as HTMLElement | null;
      input?.focus();
    }
  }
}

function addNote() {
  insertNote(model.value.length, false);
}

async function removeByIndex(index: number) {
  const prevNoteId = index > 0 ? model.value[index - 1]?.referenceId : undefined;
  const currentActive = document.activeElement as HTMLElement | null;
  const isCurrentlyInTextarea = currentActive?.tagName === "TEXTAREA";

  model.value.splice(index, 1);

  if (prevNoteId) {
    await nextTick();
    const rootEl = document.querySelector(`[data-note-id="${prevNoteId}"]`);
    if (rootEl) {
      if (isCurrentlyInTextarea) {
        const textarea = rootEl.querySelector("textarea") as HTMLTextAreaElement | null;
        if (textarea) {
          textarea.focus();
          textarea.select?.();
          return;
        }
      }
      const input = (rootEl.querySelector("input") || rootEl.querySelector("textarea")) as (HTMLInputElement | HTMLTextAreaElement) | null;
      input?.focus();
      input?.select?.();
    }
  }
}

async function moveNote(index: number, direction: -1 | 1) {
  const targetIndex = index + direction;
  if (targetIndex < 0 || targetIndex >= model.value.length) {
    return;
  }
  const noteId = model.value[index]?.referenceId;
  const currentActive = document.activeElement as HTMLElement | null;
  const rootEl = noteId ? document.querySelector(`[data-note-id="${noteId}"]`) : null;
  const activeInputIndex = rootEl && currentActive && rootEl.contains(currentActive)
    ? Array.from(rootEl.querySelectorAll("input, textarea")).indexOf(currentActive)
    : -1;

  const [item] = model.value.splice(index, 1);
  model.value.splice(targetIndex, 0, item);

  if (noteId) {
    await nextTick();
    const newRootEl = document.querySelector(`[data-note-id="${noteId}"]`);
    if (newRootEl) {
      if (activeInputIndex >= 0) {
        const inputs = Array.from(newRootEl.querySelectorAll("input, textarea")) as (HTMLInputElement | HTMLTextAreaElement)[];
        if (inputs[activeInputIndex]) {
          inputs[activeInputIndex].focus();
          return;
        }
      }
      if (document.activeElement === document.body || !newRootEl.contains(document.activeElement)) {
        const fallbackInput = (newRootEl.querySelector("input") || newRootEl.querySelector("textarea")) as HTMLElement | null;
        fallbackInput?.focus();
      }
    }
  }
}

function ensureReferenceIds() {
  model.value.forEach((note) => {
    if (!note.referenceId) {
      note.referenceId = uuid4();
    }
  });
}

onMounted(() => {
  ensureReferenceIds();
});

watch(
  model,
  () => {
    ensureReferenceIds();
  },
  { deep: true },
);
</script>
