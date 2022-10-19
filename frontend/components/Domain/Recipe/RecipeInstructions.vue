<template>
  <section @keyup.ctrl.90="undoMerge">
    <!-- Ingredient Link Editor -->
    <v-dialog v-model="dialog" width="600">
      <v-card :ripple="false">
        <v-app-bar dark color="primary" class="mt-n1 mb-3">
          <v-icon large left>
            {{ $globals.icons.link }}
          </v-icon>
          <v-toolbar-title class="headline"> {{ $t("recipe.ingredient-linker") }} </v-toolbar-title>
          <v-spacer></v-spacer>
        </v-app-bar>

        <v-card-text class="pt-4">
          <p>
            {{ activeText }}
          </p>
          <v-divider class="mb-4"></v-divider>
          <v-checkbox
            v-for="ing in unusedIngredients"
            :key="ing.referenceId"
            v-model="activeRefs"
            :value="ing.referenceId"
            class="mb-n2 mt-n2"
          >
            <template #label>
              <div v-html="parseIngredientText(ing, disableAmount)"></div>
            </template>
          </v-checkbox>

          <template v-if="usedIngredients.length > 0">
            <h4 class="py-3 ml-1">{{ $t("recipe.linked-to-other-step") }}</h4>
            <v-checkbox
              v-for="ing in usedIngredients"
              :key="ing.referenceId"
              v-model="activeRefs"
              :value="ing.referenceId"
              class="mb-n2 mt-n2"
            >
              <template #label>
                <div v-html="parseIngredientText(ing, disableAmount)"></div>
              </template>
            </v-checkbox>
          </template>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <BaseButton cancel @click="dialog = false"> </BaseButton>
          <v-spacer></v-spacer>
          <BaseButton color="info" @click="autoSetReferences">
            <template #icon> {{ $globals.icons.robot }}</template>
            {{ $t("recipe.auto") }}
          </BaseButton>
          <BaseButton save @click="setIngredientIds"> </BaseButton>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <div class="d-flex justify-space-between justify-start">
      <h2 class="mb-4 mt-1">{{ $t("recipe.instructions") }}</h2>
      <BaseButton v-if="!public && !edit && showCookMode" minor cancel color="primary" @click="toggleCookMode()">
        <template #icon>
          {{ $globals.icons.primary }}
        </template>
        {{ $t("recipe.cook-mode") }}
      </BaseButton>
    </div>
    <draggable
      :disabled="!edit"
      :value="value"
      handle=".handle"
      v-bind="{
        animation: 200,
        group: 'description',
        ghostClass: 'ghost',
      }"
      @input="updateIndex"
      @start="drag = true"
      @end="drag = false"
    >
      <TransitionGroup type="transition" :name="!drag ? 'flip-list' : ''">
        <div v-for="(step, index) in value" :key="step.id" class="list-group-item">
          <v-app-bar
            v-if="showTitleEditor[step.id]"
            class="primary mx-1 mt-6"
            style="cursor: pointer"
            dark
            dense
            rounded
            @click="toggleCollapseSection(index)"
          >
            <v-toolbar-title v-if="!edit" class="headline">
              <v-app-bar-title> {{ step.title }} </v-app-bar-title>
            </v-toolbar-title>
            <v-text-field
              v-if="edit"
              v-model="step.title"
              class="headline pa-0 mt-5"
              dense
              solo
              flat
              :placeholder="$t('recipe.section-title')"
              background-color="primary"
            >
            </v-text-field>
          </v-app-bar>
          <v-hover v-slot="{ hover }">
            <v-card
              class="ma-1"
              :class="[{ 'on-hover': hover }, isChecked(index)]"
              :elevation="hover ? 12 : 2"
              :ripple="false"
              @click="toggleDisabled(index)"
            >
              <v-card-title :class="{ 'pb-0': !isChecked(index) }">
                <span class="handle">
                  <v-icon v-if="edit" size="26" class="pb-1">{{ $globals.icons.arrowUpDown }}</v-icon>
                  {{ $t("recipe.step-index", { step: index + 1 }) }}
                </span>
                <template v-if="edit">
                  <div class="ml-auto">
                    <BaseButtonGroup
                      :large="false"
                      :buttons="[
                        {
                          icon: $globals.icons.delete,
                          text: $tc('general.delete'),
                          event: 'delete',
                        },
                        {
                          icon: $globals.icons.dotsVertical,
                          text: '',
                          event: 'open',
                          children: [
                            {
                              text: 'Toggle Section',
                              event: 'toggle-section',
                            },
                            {
                              text: 'Link Ingredients',
                              event: 'link-ingredients',
                            },
                            {
                              text: 'Merge Above',
                              event: 'merge-above',
                            },
                            {
                              icon: previewStates[index] ? $globals.icons.edit : $globals.icons.eye,
                              text: previewStates[index] ? 'Edit Markdown' : 'Preview Markdown',
                              event: 'preview-step',
                            },
                          ],
                        },
                      ]"
                      @merge-above="mergeAbove(index - 1, index)"
                      @toggle-section="toggleShowTitle(step.id)"
                      @link-ingredients="openDialog(index, step.ingredientReferences, step.text)"
                      @preview-step="togglePreviewState(index)"
                      @delete="value.splice(index, 1)"
                    />
                  </div>
                </template>
                <v-fade-transition>
                  <v-icon v-show="isChecked(index)" size="24" class="ml-auto" color="success">
                    {{ $globals.icons.checkboxMarkedCircle }}
                  </v-icon>
                </v-fade-transition>
              </v-card-title>

              <!-- Content -->
              <v-card-text
                v-if="edit"
                :class="{
                  blur: imageUploadMode,
                }"
                @drop.stop.prevent="handleImageDrop(index, $event)"
                @click="$emit('clickInstructionField', `${index}.text`)"
              >
                <MarkdownEditor
                  v-model="value[index]['text']"
                  class="mb-2"
                  :preview.sync="previewStates[index]"
                  :display-preview="false"
                  :textarea="{
                    hint: 'Attach images by dragging & dropping them into the editor',
                    persistentHint: true,
                  }"
                />

                <div
                  v-for="ing in step.ingredientReferences"
                  :key="ing.referenceId"
                  v-html="getIngredientByRefId(ing.referenceId)"
                />
              </v-card-text>
              <v-expand-transition>
                <div v-show="!isChecked(index) && !edit" class="m-0 p-0">
                  <v-card-text class="markdown">
                    <SafeMarkdown class="markdown" :source="step.text" />
                    <div v-if="cookMode && step.ingredientReferences && step.ingredientReferences.length > 0">
                      <v-divider class="mb-2"></v-divider>
                      <div
                        v-for="ing in step.ingredientReferences"
                        :key="ing.referenceId"
                        v-html="getIngredientByRefId(ing.referenceId)"
                      />
                    </div>
                  </v-card-text>
                </div>
              </v-expand-transition>
            </v-card>
          </v-hover>
        </div>
      </TransitionGroup>
    </draggable>
  </section>
</template>

<script lang="ts">
import draggable from "vuedraggable";
import {
  ref,
  toRefs,
  reactive,
  defineComponent,
  watch,
  onMounted,
  useContext,
  computed,
} from "@nuxtjs/composition-api";
import { RecipeStep, IngredientReferences, RecipeIngredient, RecipeAsset } from "~/lib/api/types/recipe";
import { parseIngredientText } from "~/composables/recipes";
import { uuid4, detectServerBaseUrl } from "~/composables/use-utils";
import { useUserApi, useStaticRoutes } from "~/composables/api";

interface MergerHistory {
  target: number;
  source: number;
  targetText: string;
  sourceText: string;
}

export default defineComponent({
  components: {
    draggable,
  },
  props: {
    value: {
      type: Array as () => RecipeStep[],
      required: true,
    },
    edit: {
      type: Boolean,
      default: true,
    },
    ingredients: {
      type: Array as () => RecipeIngredient[],
      default: () => [],
    },
    disableAmount: {
      type: Boolean,
      default: false,
    },
    public: {
      type: Boolean,
      default: false,
    },
    recipeId: {
      type: String,
      default: "",
    },
    recipeSlug: {
      type: String,
      default: "",
    },
    assets: {
      type: Array as () => RecipeAsset[],
      required: true,
    },
    cookMode: {
      type: Boolean,
      default: false,
    },
    scale: {
      type: Number,
      default: 1,
    },
  },

  setup(props, context) {
    const { i18n, req } = useContext();
    const BASE_URL = detectServerBaseUrl(req);

    console.log("Base URL", BASE_URL);

    const state = reactive({
      dialog: false,
      disabledSteps: [] as number[],
      unusedIngredients: [] as RecipeIngredient[],
      usedIngredients: [] as RecipeIngredient[],
    });

    const showTitleEditor = ref<{ [key: string]: boolean }>({});

    const actionEvents = [
      {
        text: i18n.t("recipe.toggle-section") as string,
        event: "toggle-section",
      },
      {
        text: i18n.t("recipe.link-ingredients") as string,
        event: "link-ingredients",
      },
      {
        text: i18n.t("recipe.merge-above") as string,
        event: "merge-above",
      },
    ];

    // ===============================================================
    // UI State Helpers

    function validateTitle(title: string | undefined) {
      return !(title === null || title === "" || title === undefined);
    }

    watch(props.value, (v) => {
      state.disabledSteps = [];

      v.forEach((element: RecipeStep) => {
        if (element.id !== undefined) {
          showTitleEditor.value[element.id] = validateTitle(element.title);
        }
      });
    });

    const showCookMode = ref(false);

    // Eliminate state with an eager call to watcher?
    onMounted(() => {
      props.value.forEach((element: RecipeStep) => {
        if (element.id !== undefined) {
          showTitleEditor.value[element.id] = validateTitle(element.title);
        }

        // showCookMode.value = false;
        if (showCookMode.value === false && element.ingredientReferences && element.ingredientReferences.length > 0) {
          showCookMode.value = true;
        }

        showTitleEditor.value = { ...showTitleEditor.value };
      });
    });

    function toggleDisabled(stepIndex: number) {
      if (props.edit) {
        return;
      }
      if (state.disabledSteps.includes(stepIndex)) {
        const index = state.disabledSteps.indexOf(stepIndex);
        if (index !== -1) {
          state.disabledSteps.splice(index, 1);
        }
      } else {
        state.disabledSteps.push(stepIndex);
      }
    }

    function isChecked(stepIndex: number) {
      if (state.disabledSteps.includes(stepIndex) && !props.edit) {
        return "disabled-card";
      }
    }

    function toggleShowTitle(id: string) {
      showTitleEditor.value[id] = !showTitleEditor.value[id];

      const temp = { ...showTitleEditor.value };
      showTitleEditor.value = temp;
    }

    function updateIndex(data: RecipeStep) {
      context.emit("input", data);
    }

    // ===============================================================
    // Ingredient Linker
    const activeRefs = ref<string[]>([]);
    const activeIndex = ref(0);
    const activeText = ref("");

    function openDialog(idx: number, refs: IngredientReferences[], text: string) {
      setUsedIngredients();
      activeText.value = text;
      activeIndex.value = idx;
      state.dialog = true;
      activeRefs.value = refs.map((ref) => ref.referenceId ?? "");
    }

    function setIngredientIds() {
      const instruction = props.value[activeIndex.value];
      instruction.ingredientReferences = activeRefs.value.map((ref) => {
        return {
          referenceId: ref,
        };
      });

      // Update the visibility of the cook mode button
      showCookMode.value = false;
      props.value.forEach((element) => {
        if (showCookMode.value === false && element.ingredientReferences && element.ingredientReferences.length > 0) {
          showCookMode.value = true;
        }
      });
      state.dialog = false;
    }

    function setUsedIngredients() {
      const usedRefs: { [key: string]: boolean } = {};

      props.value.forEach((element) => {
        element.ingredientReferences?.forEach((ref) => {
          if (ref.referenceId !== undefined) {
            usedRefs[ref.referenceId] = true;
          }
        });
      });

      state.usedIngredients = props.ingredients.filter((ing) => {
        return ing.referenceId !== undefined && ing.referenceId in usedRefs;
      });

      state.unusedIngredients = props.ingredients.filter((ing) => {
        return !(ing.referenceId !== undefined && ing.referenceId in usedRefs);
      });
    }

    function autoSetReferences() {
      // Ignore matching blacklisted words when auto-linking - This is kind of a cludgey implementation. We're blacklisting common words but
      // other common phrases trigger false positives and I'm not sure how else to approach this. In the future I maybe look at looking directly
      // at the food variable and seeing if the food is in the instructions, but I still need to support those who don't want to provide the value
      // and only use the "notes" feature.
      const blackListedText = [
        "and",
        "or",
        "the",
        "a",
        "an",
        "of",
        "in",
        "on",
        "to",
        "for",
        "by",
        "with",
        "without",
        "",
        " ",
      ];
      const blackListedRegexMatch = /\d/gm; // Match Any Number

      // Check if any of the words in the active text match the ingredient text
      const instructionsByWord = activeText.value.toLowerCase().split(" ");

      instructionsByWord.forEach((word) => {
        if (blackListedText.includes(word) || word.match(blackListedRegexMatch)) {
          return;
        }

        props.ingredients.forEach((ingredient) => {
          const searchText = parseIngredientText(ingredient, props.disableAmount);

          if (ingredient.referenceId === undefined) {
            return;
          }

          if (searchText.toLowerCase().includes(" " + word) && !activeRefs.value.includes(ingredient.referenceId)) {
            console.info("Word Matched", `'${word}'`, ingredient.note);
            activeRefs.value.push(ingredient.referenceId);
          }
        });
      });
    }

    const ingredientLookup = computed(() => {
      const results: { [key: string]: RecipeIngredient } = {};
      return props.ingredients.reduce((prev, ing) => {
        if (ing.referenceId === undefined) {
          return prev;
        }
        prev[ing.referenceId] = ing;
        return prev;
      }, results);
    });

    function getIngredientByRefId(refId: string | undefined) {
      if (refId === undefined) {
        return "";
      }

      const ing = ingredientLookup.value[refId] ?? "";
      if (ing === "") {
        return "";
      }
      return parseIngredientText(ing, props.disableAmount, props.scale);
    }

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
        targetText: props.value[target].text,
        sourceText: props.value[source].text,
      });

      props.value[target].text += " " + props.value[source].text;
      props.value.splice(source, 1);
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

        props.value[lastMerge.target].text = lastMerge.targetText;
        props.value.splice(lastMerge.source, 0, {
          id: uuid4(),
          title: "",
          text: lastMerge.sourceText,
          ingredientReferences: [],
        });
      }
    }

    const previewStates = ref<boolean[]>([]);

    function togglePreviewState(index: number) {
      const temp = [...previewStates.value];
      temp[index] = !temp[index];
      previewStates.value = temp;
    }

    function toggleCollapseSection(index: number) {
      const sectionSteps: number[] = [];

      for (let i = index; i < props.value.length; i++) {
        if (!(i === index) && validateTitle(props.value[i].title)) {
          break;
        } else {
          sectionSteps.push(i);
        }
      }

      const allCollapsed = sectionSteps.every((idx) => state.disabledSteps.includes(idx));

      if (allCollapsed) {
        state.disabledSteps = state.disabledSteps.filter((idx) => !sectionSteps.includes(idx));
      } else {
        state.disabledSteps = [...state.disabledSteps, ...sectionSteps];
      }
    }

    const drag = ref(false);

    // ===============================================================
    // Image Uploader
    const api = useUserApi();
    const { recipeAssetPath } = useStaticRoutes();

    const imageUploadMode = ref(false);

    function toggleDragMode() {
      console.log("Toggling Drag Mode");
      imageUploadMode.value = !imageUploadMode.value;
    }

    onMounted(() => {
      if (props.assets === undefined) {
        context.emit("update:assets", []);
      }
    });

    async function handleImageDrop(index: number, e: DragEvent) {
      if (!e.dataTransfer) {
        return;
      }

      // Check if the file is an image
      const file = e.dataTransfer.files[0];
      if (!file || !file.type.startsWith("image/")) {
        return;
      }

      const { data } = await api.recipes.createAsset(props.recipeSlug, {
        name: file.name,
        icon: "mdi-file-image",
        file,
        extension: file.name.split(".").pop() || "",
      });

      if (!data) {
        return; // TODO: Handle error
      }

      context.emit("update:assets", [...props.assets, data]);
      const assetUrl = BASE_URL + recipeAssetPath(props.recipeId, data.fileName as string);
      const text = `<img src="${assetUrl}" height="100%" width="100%"/>`;
      props.value[index].text += text;
    }

    function toggleCookMode() {
      context.emit("cookModeToggle");
    }

    return {
      // Image Uploader
      toggleDragMode,
      handleImageDrop,
      imageUploadMode,

      // Rest
      drag,
      togglePreviewState,
      toggleCollapseSection,
      previewStates,
      ...toRefs(state),
      actionEvents,
      activeRefs,
      activeText,
      getIngredientByRefId,
      showTitleEditor,
      mergeAbove,
      openDialog,
      setIngredientIds,
      undoMerge,
      toggleDisabled,
      isChecked,
      toggleShowTitle,
      updateIndex,
      autoSetReferences,
      parseIngredientText,
      toggleCookMode,
      showCookMode,
    };
  },
});
</script>

<style lang="css" scoped>
.v-card--link:before {
  background: none;
}

/** Select all li under .markdown class */
.markdown >>> ul > li {
  display: list-item;
  list-style-type: disc !important;
}

/** Select all li under .markdown class */
.markdown >>> ol > li {
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
.list-group-item {
  cursor: move;
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
</style>
