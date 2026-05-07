<template>
  <section @keyup.ctrl.z="undoMerge">
    <!-- Ingredient Link Editor -->
    <BaseDialog
      v-model="dialog"
      :title="$t('recipe.link-references')"
      :icon="$globals.icons.link"
      width="100%"
      max-width="600px"
      max-height="60%"
    >
      <div class="grid">
        <div class="sticky">
          <v-card flat style="max-height: 40dvh; overflow-y: auto;">
            <v-card-text class="pt-4">
              <p>
                {{ activeDialogStepText }}
              </p>
              <v-divider class="my-4" />

              <h4 class="ml-1">
                {{ $t("recipe.ingredients") }}
              </h4>
            </v-card-text>
          </v-card>
          <v-divider />
        </div>
        <v-card flat>
          <v-card-text>
            <template v-if="Object.keys(groupedUnusedIngredients).length > 0">
              <h4 class="ml-1">
                {{ $t("recipe.unlinked") }}
              </h4>
              <template v-for="(ingredients, title) in groupedUnusedIngredients" :key="title">
                <h4 v-if="title" class="py-3 ml-1 pl-4">
                  {{ title }}
                </h4>
                <v-checkbox-btn
                  v-for="ing in ingredients"
                  :key="ing.referenceId"
                  v-model="activeRefs"
                  :value="ing.referenceId"
                  class="ml-4"
                >
                  <template #label>
                    <RecipeIngredientHtml :ingredient="ing" :scale="scale" />
                  </template>
                </v-checkbox-btn>
              </template>
            </template>

            <template v-if="Object.keys(groupedUsedIngredients).length > 0">
              <h4 class="py-3 ml-1">
                {{ $t("recipe.linked-to-other-step") }}
              </h4>
              <template v-for="(ingredients, title) in groupedUsedIngredients" :key="title">
                <h4 v-if="title" class="py-3 ml-1 pl-4">
                  {{ title }}
                </h4>
                <v-checkbox-btn
                  v-for="ing in ingredients"
                  :key="ing.referenceId"
                  v-model="activeRefs"
                  :value="ing.referenceId"
                  class="ml-4"
                >
                  <template #label>
                    <RecipeIngredientHtml :ingredient="ing" :scale="scale" />
                  </template>
                </v-checkbox-btn>
              </template>
            </template>

            <v-divider class="my-4" />

            <h4 class="ml-1 mb-2">
              {{ $t("recipe.notes") }}
            </h4>
            <p v-if="linkableNotes.length === 0" class="text-body-2 text-medium-emphasis">
              {{ $t('recipe.no-notes-to-link') }}
            </p>
            <v-checkbox-btn
              v-for="note in linkableNotes"
              :key="note.referenceId"
              v-model="activeNoteReferenceIds"
              :value="note.referenceId"
              class="ml-4"
            >
              <template #label>
                {{ note.title || $t('recipe.note') }}
              </template>
            </v-checkbox-btn>
          </v-card-text>
        </v-card>
      </div>

      <v-divider />

      <template #card-actions>
        <div class="d-flex flex-grow-1">
          <BaseButton
            cancel
            @click="closeDialog"
          />
          <v-spacer />
          <div class="d-flex flex-wrap justify-end ga-2">
            <BaseButton
              color="info"
              @click="autoSetReferences"
            >
              <template #icon>
                {{ $globals.icons.robot }}
              </template>
              {{ $t("recipe.auto") }}
            </BaseButton>
            <BaseButton
              save
              @click="saveDialogLinks"
            />
            <BaseButton
              v-if="availableDialogNextStep"
              class="ml-2 my-1"
              @click="saveAndOpenNextDialogLinks"
            >
              <template #icon>
                {{ $globals.icons.forward }}
              </template>
              {{ $t("recipe.nextStep") }}
            </BaseButton>
          </div>
        </div>
      </template>
    </BaseDialog>

    <div class="d-flex justify-space-between justify-start">
      <h2
        v-if="!isCookMode"
        class="mt-1 text-h5 font-weight-medium opacity-80"
      >
        {{ $t("recipe.instructions") }}
      </h2>
      <BaseButton
        v-if="!isEditForm && !isCookMode"
        minor
        cancel
        color="primary"
        @click="toggleCookMode()"
      >
        <template #icon>
          {{ $globals.icons.primary }}
        </template>
        {{ $t("recipe.cook-mode") }}
      </BaseButton>
    </div>
    <VueDraggable
      v-model="instructionList"
      :disabled="!isEditForm"
      handle=".handle"
      :delay="250"
      :delay-on-touch-only="true"
      v-bind="{
        animation: 200,
        group: 'recipe-instructions',
        ghostClass: 'ghost',
      }"
      @start="drag = true"
      @end="onDragEnd"
    >
      <TransitionGroup
        type="transition"
      >
        <div
          v-for="(step, index) in instructionList"
          :key="step.id!"
          class="list-group-item"
        >
          <v-sheet
            v-if="step.id && showTitleEditor[step.id]"
            color="primary"
            class="mt-6 mb-2 d-flex align-center"
            :class="isEditForm ? 'pa-2' : 'pa-3'"
            style="border-radius: 6px; cursor: pointer; width: 100%;"
            @click="toggleCollapseSection(index)"
          >
            <template v-if="isEditForm">
              <v-text-field
                v-model="step.title"
                class="pa-0"
                density="compact"
                variant="solo"
                flat
                :placeholder="$t('recipe.section-title')"
                bg-color="primary"
                hide-details
              />
            </template>
            <template v-else>
              <v-toolbar-title class="section-title-text">
                {{ step.title }}
              </v-toolbar-title>
            </template>
          </v-sheet>
          <v-hover v-slot="{ isHovering }">
            <v-card
              class="my-3"
              :class="[{ 'on-hover': isHovering }, { 'cursor-default': isEditForm }, isChecked(index)]"
              :elevation="isHovering ? 12 : 2"
              :ripple="false"
              @click="toggleDisabled(index)"
            >
              <v-card-title class="recipe-step-title pt-3" :class="!isChecked(index) ? 'pb-0' : 'pb-3'">
                <div class="d-flex align-center w-100">
                  <v-text-field
                    v-if="isEditForm"
                    v-model="step.summary"
                    class="headline"
                    hide-details
                    density="compact"
                    variant="solo"
                    flat
                    :placeholder="$t('recipe.step-index', { step: index + 1 })"
                  >
                    <template #prepend>
                      <v-icon size="26" class="handle">
                        {{ $globals.icons.arrowUpDown }}
                      </v-icon>
                    </template>
                  </v-text-field>
                  <div
                    v-else
                    class="summary-wrapper"
                  >
                    <template v-if="step.summary">
                      <SafeMarkdown
                        class="pr-2"
                        :source="step.summary"
                      />
                    </template>
                    <template v-else>
                      <span>
                        {{ $t('recipe.step-index', { step: index + 1 }) }}
                      </span>
                    </template>
                  </div>
                  <template v-if="isEditForm">
                    <div class="ml-auto">
                      <BaseButtonGroup
                        :large="false"
                        :buttons="[
                          {
                            icon: $globals.icons.delete,
                            text: $t('general.delete'),
                            event: 'delete',
                          },
                          {
                            icon: $globals.icons.dotsVertical,
                            text: '',
                            event: 'open',
                            children: [
                              {
                                text: $t('recipe.toggle-section'),
                                event: 'toggle-section',
                              },
                              {
                                text: $t('recipe.link-references'),
                                event: 'link-references',
                              },
                              {
                                text: $t('recipe.upload-image'),
                                event: 'upload-image',
                              },
                              {
                                icon: previewStates[index] ? $globals.icons.edit : $globals.icons.eye,
                                text: previewStates[index] ? $t('recipe.edit-markdown') : $t('markdown-editor.preview-markdown-button-label'),
                                event: 'preview-step',
                                divider: true,
                              },
                              {
                                text: $t('recipe.merge-above'),
                                event: 'merge-above',
                              },
                              {
                                text: $t('recipe.move-to-top'),
                                event: 'move-to-top',
                              },
                              {
                                text: $t('recipe.move-to-bottom'),
                                event: 'move-to-bottom',
                              },
                              {
                                text: $t('recipe.insert-above'),
                                event: 'insert-above',
                              },
                              {
                                text: $t('recipe.insert-below'),
                                event: 'insert-below',
                              },
                            ],
                          },
                        ]"
                        @merge-above="mergeAbove(index - 1, index)"
                        @move-to-top="moveTo('top', index)"
                        @move-to-bottom="moveTo('bottom', index)"
                        @insert-above="insert(index)"
                        @insert-below="insert(index + 1)"
                        @toggle-section="toggleShowTitle(step.id!)"
                        @link-references="openReferenceDialog(index)"
                        @preview-step="togglePreviewState(index)"
                        @upload-image="openImageUpload(index)"
                        @delete="instructionList.splice(index, 1)"
                      />
                    </div>
                  </template>
                  <div v-if="!isEditForm" class="ml-auto d-flex align-center gap-1">
                    <v-fade-transition>
                      <v-icon
                        v-show="isChecked(index)"
                        size="24"
                        color="success"
                      >
                        {{ $globals.icons.checkboxMarkedCircle }}
                      </v-icon>
                    </v-fade-transition>
                  </div>
                </div>
              </v-card-title>

              <v-progress-linear
                v-if="isEditForm && loadingStates[index]"
                :active="true"
                :indeterminate="true"
              />

              <!-- Content -->
              <DropZone @drop="(f) => handleImageDrop(index, f)">
                <v-card-text
                  v-if="isEditForm"
                  @click="$emit('click-instruction-field', `${index}.text`)"
                >
                  <MarkdownEditor
                    v-model="instructionList[index]['text']"
                    v-model:preview="previewStates[index]"
                    class="mb-2"
                    :display-preview="false"
                    :textarea="{
                      hint: $t('recipe.attach-images-hint'),
                      persistentHint: true,
                    }"
                  />
                  <div
                    v-if="step.ingredientReferences && step.ingredientReferences.length"
                    class="linked-ingredients-editor"
                  >
                    <div
                      v-for="(linkRef, i) in step.ingredientReferences"
                      :key="linkRef.referenceId ?? i"
                      class="mb-1"
                    >
                      <RecipeIngredientHtml
                        v-if="linkRef.referenceId && ingredientLookup[linkRef.referenceId]"
                        :ingredient="ingredientLookup[linkRef.referenceId]"
                        :scale="scale"
                      />
                    </div>
                  </div>
                  <div
                    v-if="step.noteReferences && step.noteReferences.length"
                    class="linked-ingredients-editor mt-1"
                  >
                    <div
                      v-for="(noteRef, i) in step.noteReferences"
                      :key="noteRef.referenceId ?? i"
                      class="mb-1 d-flex align-center text-body-2"
                    >
                      <v-icon size="14" class="mr-1" style="cursor: default;">
                        {{ $globals.icons.noteTextOutline }}
                      </v-icon>
                      {{ noteRef.referenceId != null ? noteLookup[noteRef.referenceId] : '' }}
                    </div>
                  </div>
                </v-card-text>
              </DropZone>
              <v-expand-transition>
                <div
                  v-if="!isChecked(index) && !isEditForm"
                  class="m-0 p-0"
                >
                  <v-card-text class="markdown">
                    <v-row>
                      <v-col
                        v-if="isCookMode && hasCookModeLinkedContent(step)"
                        cols="12"
                        sm="5"
                      >
                        <div
                          v-if="hasLinkedIngredients(step)"
                          class="ml-n4"
                        >
                          <RecipeIngredients
                            :value="recipe.recipeIngredient.filter((ing) => {
                              if (!step.ingredientReferences) return false
                              return step.ingredientReferences.map((ref) => ref.referenceId).includes(ing.referenceId || '')
                            })"
                            :scale="scale"
                            :is-cook-mode="isCookMode"
                          />
                        </div>
                        <v-divider
                          v-if="hasLinkedIngredients(step) && hasLinkedNotes(step)"
                          class="my-3"
                        />
                        <div v-if="hasLinkedNotes(step)">
                          <template
                            v-for="(note, noteIndex) in linkedNotesForStep(step)"
                            :key="note.referenceId ?? note.title"
                          >
                            <v-divider
                              v-if="noteIndex > 0"
                              class="my-3"
                            />
                            <div class="text-title-large mb-1">
                              {{ note.title }}
                            </div>
                            <SafeMarkdown :source="note.text" />
                          </template>
                        </div>
                      </v-col>
                      <v-divider
                        v-if="isCookMode && hasCookModeLinkedContent(step) && $vuetify.display.smAndUp"
                        vertical
                      />
                      <v-col>
                        <SafeMarkdown
                          class="markdown"
                          :source="step.text"
                        />
                      </v-col>
                    </v-row>
                  </v-card-text>
                </div>
              </v-expand-transition>
            </v-card>
          </v-hover>
        </div>
      </TransitionGroup>
    </VueDraggable>
    <v-divider
      v-if="!isCookMode"
      class="mt-10 d-flex d-md-none"
    />
  </section>
</template>

<script setup lang="ts">
import { VueDraggable } from "vue-draggable-plus";
import { computed, nextTick, onMounted, ref, watch } from "vue";
import type { RecipeStep, RecipeNote, RecipeIngredient, RecipeAsset, Recipe } from "~/lib/api/types/recipe";
import { uuid4 } from "~/composables/use-utils";
import { useUserApi, useStaticRoutes } from "~/composables/api";
import { usePageState } from "~/composables/recipe-page/shared-state";
import { useExtractIngredientReferences } from "~/composables/recipe-page/use-extract-ingredient-references";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import DropZone from "~/components/global/DropZone.vue";
import RecipeIngredients from "~/components/Domain/Recipe/RecipeIngredients.vue";
import RecipeIngredientHtml from "~/components/Domain/Recipe/RecipeIngredientHtml.vue";

interface MergerHistory {
  target: number;
  source: number;
  targetText: string;
  sourceText: string;
}

const instructionList = defineModel<RecipeStep[]>("modelValue", { required: true, default: () => [] });
const assets = defineModel<RecipeAsset[]>("assets", { required: true, default: () => [] });

const props = defineProps({
  recipe: {
    type: Object as () => NoUndefinedField<Recipe>,
    required: true,
  },
  scale: {
    type: Number,
    default: 1,
  },
});

const emit = defineEmits(["click-instruction-field", "update:assets"]);

const { isCookMode, toggleCookMode, isEditForm } = usePageState(props.recipe.slug);
const { extractIngredientReferences } = useExtractIngredientReferences();

const dialog = ref(false);
const disabledSteps = ref<number[]>([]);
const unusedIngredients = ref<RecipeIngredient[]>([]);
const usedIngredients = ref<RecipeIngredient[]>([]);

const showTitleEditor = ref<{ [key: string]: boolean }>({});

// ===============================================================
// UI State Helpers

function hasSectionTitle(title: string | undefined) {
  return !(title === null || title === "" || title === undefined);
}

watch(instructionList, (v) => {
  disabledSteps.value = [];

  v.forEach((element: RecipeStep) => {
    if (element.id !== undefined) {
      showTitleEditor.value[element.id!] = hasSectionTitle(element.title!);
    }
  });
}, { deep: true });

const showCookMode = ref(false);

onMounted(() => {
  instructionList.value.forEach((element: RecipeStep) => {
    if (element.id !== undefined) {
      showTitleEditor.value[element.id!] = hasSectionTitle(element.title!);
    }

    if (showCookMode.value === false && element.ingredientReferences && element.ingredientReferences.length > 0) {
      showCookMode.value = true;
    }

    showTitleEditor.value = { ...showTitleEditor.value };
  });

  if (assets.value === undefined) {
    emit("update:assets", []);
  }
});

function toggleDisabled(stepIndex: number) {
  if (isEditForm.value) {
    return;
  }
  if (disabledSteps.value.includes(stepIndex)) {
    const index = disabledSteps.value.indexOf(stepIndex);
    if (index !== -1) {
      disabledSteps.value.splice(index, 1);
    }
  }
  else {
    disabledSteps.value.push(stepIndex);
  }
}

function isChecked(stepIndex: number) {
  if (disabledSteps.value.includes(stepIndex) && !isEditForm.value) {
    return "disabled-card";
  }
}

function toggleShowTitle(id?: string) {
  if (!id) {
    return;
  }

  showTitleEditor.value[id] = !showTitleEditor.value[id];

  const temp = { ...showTitleEditor.value };
  showTitleEditor.value = temp;
}

function onDragEnd() {
  drag.value = false;
}

// ===============================================================
// Reference Linker
const activeLinkerIndex = ref(0);
const activeRefs = ref<string[]>([]);
const activeNoteReferenceIds = ref<string[]>([]);
const activeText = ref("");

const availableDialogNextStep = computed(() => activeLinkerIndex.value < instructionList.value.length - 1);
const activeDialogStepText = computed(() => activeText.value);
const linkableNotes = computed(() => {
  return (props.recipe.notes ?? []).filter((note): note is RecipeNote & { referenceId: string } => note.referenceId != null);
});

function openReferenceDialog(idx: number) {
  activeLinkerIndex.value = idx;
  const step = instructionList.value[idx];

  if (!step) {
    activeRefs.value = [];
    activeNoteReferenceIds.value = [];
    return;
  }

  activeText.value = step.text;
  setUsedIngredients();
  activeRefs.value = (step.ingredientReferences ?? []).map(ref => ref.referenceId ?? "");
  activeNoteReferenceIds.value = (step.noteReferences ?? [])
    .map(ref => ref.referenceId)
    .filter((ref): ref is string => ref != null);
  dialog.value = true;
}

function updateCookModeVisibility() {
  showCookMode.value = false;
  instructionList.value.forEach((element) => {
    if (showCookMode.value === false && element.ingredientReferences && element.ingredientReferences.length > 0) {
      showCookMode.value = true;
    }
  });
}

function saveDialogLinks() {
  const step = instructionList.value[activeLinkerIndex.value];

  if (!step) {
    dialog.value = false;
    return;
  }

  step.ingredientReferences = activeRefs.value.map((referenceId) => {
    return { referenceId };
  });

  step.noteReferences = activeNoteReferenceIds.value.map((referenceId) => {
    return { referenceId };
  });

  updateCookModeVisibility();
  dialog.value = false;
}

function saveAndOpenNextDialogLinks() {
  const currentStepIndex = activeLinkerIndex.value;

  if (!availableDialogNextStep.value) {
    return;
  }

  saveDialogLinks();
  nextTick(() => openReferenceDialog(currentStepIndex + 1));
}

function closeDialog() {
  dialog.value = false;
}

function setUsedIngredients() {
  const usedRefs: { [key: string]: boolean } = {};

  instructionList.value.forEach((element, idx) => {
    if (idx === activeLinkerIndex.value) return;
    element.ingredientReferences?.forEach((ref) => {
      if (ref.referenceId) usedRefs[ref.referenceId] = true;
    });
  });

  usedIngredients.value = props.recipe.recipeIngredient.filter(ing => !!ing.referenceId && ing.referenceId in usedRefs);

  unusedIngredients.value = props.recipe.recipeIngredient.filter(ing => !!ing.referenceId && !(ing.referenceId in usedRefs));
}

watch(activeRefs, () => setUsedIngredients());

function autoSetReferences() {
  extractIngredientReferences(
    props.recipe.recipeIngredient,
    activeRefs.value,
    activeText.value,
  ).forEach(ingredient => activeRefs.value.push(ingredient));
}

const noteLookup = computed(() => {
  const results: { [key: string]: string } = {};
  return (props.recipe.notes ?? []).reduce((prev, note) => {
    if (note.referenceId != null) {
      prev[note.referenceId] = note.title;
    }
    return prev;
  }, results);
});

const notesByReferenceId = computed(() => {
  const results: { [key: string]: RecipeNote } = {};
  return (props.recipe.notes ?? []).reduce((prev, note) => {
    if (note.referenceId != null) {
      prev[note.referenceId] = note;
    }
    return prev;
  }, results);
});

function linkedNotesForStep(step: RecipeStep): RecipeNote[] {
  return (step.noteReferences ?? [])
    .map(ref => ref.referenceId ? notesByReferenceId.value[ref.referenceId] : undefined)
    .filter((note): note is RecipeNote => note !== undefined);
}

function hasLinkedIngredients(step: RecipeStep): boolean {
  return !!step.ingredientReferences && step.ingredientReferences.length > 0;
}

function hasLinkedNotes(step: RecipeStep): boolean {
  return linkedNotesForStep(step).length > 0;
}

function hasCookModeLinkedContent(step: RecipeStep): boolean {
  return hasLinkedIngredients(step) || hasLinkedNotes(step);
}

const ingredientLookup = computed(() => {
  const results: { [key: string]: RecipeIngredient } = {};
  return props.recipe.recipeIngredient.reduce((prev, ing) => {
    if (ing.referenceId === undefined) {
      return prev;
    }
    prev[ing.referenceId] = ing;
    return prev;
  }, results);
});

// Map each ingredient's referenceId to its section title
const ingredientSectionTitles = computed(() => {
  const titleMap: { [key: string]: string } = {};
  let currentTitle = "";

  // Go through all ingredients in order
  props.recipe.recipeIngredient.forEach((ingredient) => {
    if (ingredient.referenceId === undefined) {
      return;
    }

    // If this ingredient has a title, update the current title
    if (ingredient.title) {
      currentTitle = ingredient.title;
    }

    // Assign the current title to this ingredient
    titleMap[ingredient.referenceId] = currentTitle;
  });

  return titleMap;
});

const groupedUnusedIngredients = computed((): Record<string, RecipeIngredient[]> => {
  const groups: Record<string, RecipeIngredient[]> = {};

  // Group ingredients by section title
  unusedIngredients.value.forEach((ingredient) => {
    if (ingredient.referenceId === undefined) {
      return;
    }

    // Use the section title from the mapping, or fallback to the ingredient's own title
    const title = ingredientSectionTitles.value[ingredient.referenceId] || ingredient.title || "";
    (groups[title] ||= []).push(ingredient);
  });

  return groups;
});

const groupedUsedIngredients = computed((): Record<string, RecipeIngredient[]> => {
  const groups: Record<string, RecipeIngredient[]> = {};
  usedIngredients.value.forEach((ingredient) => {
    if (ingredient.referenceId === undefined) {
      return;
    }

    // Use the section title from the mapping, or fallback to the ingredient's own title
    const title = ingredientSectionTitles.value[ingredient.referenceId] || ingredient.title || "";
    (groups[title] ||= []).push(ingredient);
  });

  return groups;
});

// ===============================================================
// Instruction Merger
const mergeHistory = ref<MergerHistory[]>([]);

function mergeAbove(target: number, source: number) {
  if (target < 0) {
    return;
  }

  mergeHistory.value.push({
    target,
    source,
    targetText: instructionList.value[target].text,
    sourceText: instructionList.value[source].text,
  });

  instructionList.value[target].text += " " + instructionList.value[source].text;
  instructionList.value.splice(source, 1);
}

function undoMerge(event: KeyboardEvent) {
  if (event.ctrlKey && event.code === "KeyZ") {
    if (!(mergeHistory.value?.length > 0)) {
      return;
    }

    const lastMerge = mergeHistory.value.pop();
    if (!lastMerge) {
      return;
    }

    instructionList.value[lastMerge.target].text = lastMerge.targetText;
    instructionList.value.splice(lastMerge.source, 0, {
      id: uuid4(),
      title: "",
      text: lastMerge.sourceText,
      ingredientReferences: [],
      noteReferences: [],
    });
  }
}

function moveTo(dest: string, source: number) {
  if (dest === "top") {
    instructionList.value.unshift(instructionList.value.splice(source, 1)[0]);
  }
  else {
    instructionList.value.push(instructionList.value.splice(source, 1)[0]);
  }
}

function insert(dest: number) {
  instructionList.value.splice(dest, 0, { id: uuid4(), text: "", title: "", ingredientReferences: [], noteReferences: [] });
}

const previewStates = ref<boolean[]>([]);

function togglePreviewState(index: number) {
  const temp = [...previewStates.value];
  temp[index] = !temp[index];
  previewStates.value = temp;
}

function toggleCollapseSection(index: number) {
  const sectionSteps: number[] = [];

  for (let i = index; i < instructionList.value.length; i++) {
    if (!(i === index) && hasSectionTitle(instructionList.value[i].title!)) {
      break;
    }
    else {
      sectionSteps.push(i);
    }
  }

  const allCollapsed = sectionSteps.every(idx => disabledSteps.value.includes(idx));

  if (allCollapsed) {
    disabledSteps.value = disabledSteps.value.filter(idx => !sectionSteps.includes(idx));
  }
  else {
    disabledSteps.value = [...disabledSteps.value, ...sectionSteps];
  }
}

const drag = ref(false);

// ===============================================================
// Image Uploader
const api = useUserApi();
const { recipeAssetPath } = useStaticRoutes();

const loadingStates = ref<{ [key: number]: boolean }>({});

async function handleImageDrop(index: number, files: File[]) {
  if (!files) {
    return;
  }

  // Check if the file is an image
  const file = files[0];
  if (!file || !file.type.startsWith("image/")) {
    return;
  }

  loadingStates.value[index] = true;

  const { data } = await api.recipes.createAsset(props.recipe.slug, {
    name: file.name,
    icon: "mdi-file-image",
    file,
    extension: file.name.split(".").pop() || "",
  });

  loadingStates.value[index] = false;

  if (!data) {
    return; // TODO: Handle error
  }

  emit("update:assets", [...assets.value, data]);
  const assetUrl = recipeAssetPath(props.recipe.id, data.fileName as string);
  const text = `<img src="${assetUrl}" height="100%" width="100%"/>`;
  instructionList.value[index].text += text;
}

function openImageUpload(index: number) {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = "image/*";
  input.onchange = async () => {
    if (input.files) {
      await handleImageDrop(index, Array.from(input.files));
      input.remove();
    }
  };
  input.click();
}
</script>

<style lang="css" scoped>
.grid {
  display: grid;
  gap: 0.5rem;
  height: 100%;
  box-sizing: border-box;

  > * {
    overflow-y: auto;
  }
}

.sticky {
  position: sticky;
  top: 0;
  z-index: 2;
}

.v-card--link:before {
  background: none;
}

/** Select all li under .markdown class */
.markdown :deep(ul > li) {
  display: list-item;
  list-style-type: disc !important;
}

/** Select all li under .markdown class */
.markdown :deep(ol > li) {
  display: list-item;
}

.flip-list-move {
  transition: transform 0.5s;
}

.no-move {
  transition: transform 0s;
}

.ghost {
  opacity: 0.5;
}

.list-group {
  min-height: 38px;
}

.list-group-item i {
  cursor: pointer;
}

.blur {
  filter: blur(2px);
}

.upload-overlay {
  display: flex;
  justify-content: center;
  align-items: center;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1;
}

.v-text-field :deep(input) {
  font-size: 1.5rem;
}

.v-card-text {
  font-size: 1rem;
}

.recipe-step-title {
  /* Multiline display */
  white-space: normal;
  line-height: 1.25;
  word-break: break-word;
}
.summary-wrapper {
  flex: 1 1 auto;
  min-width: 0; /* wrapping in flex container */
  white-space: normal;
  overflow-wrap: anywhere;
  cursor: pointer;
}
</style>
