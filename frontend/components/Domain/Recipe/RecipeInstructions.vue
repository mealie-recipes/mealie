<template>
  <section @keyup.ctrl.90="undoMerge">
    <!-- Ingredient Link Editor -->
    <v-dialog v-model="dialog" width="600">
      <v-card>
        <v-app-bar dark color="primary" class="mt-n1 mb-3">
          <v-icon large left>
            {{ $globals.icons.link }}
          </v-icon>
          <v-toolbar-title class="headline"> Ingredient Linker </v-toolbar-title>
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

          <h4 class="py-3 ml-1">Linked to other step</h4>
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
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <BaseButton cancel @click="dialog = false"> </BaseButton>
          <v-spacer></v-spacer>
          <BaseButton color="info" @click="autoSetReferences">
            <template #icon> {{ $globals.icons.robot }}</template>
            Auto
          </BaseButton>
          <BaseButton save @click="setIngredientIds"> </BaseButton>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <div class="d-flex justify-space-between justify-start">
      <h2 class="mb-4 mt-1">{{ $t("recipe.instructions") }}</h2>
      <BaseButton minor :to="$router.currentRoute.path + '/cook'" cancel color="primary">
        <template #icon>
          {{ $globals.icons.primary }}
        </template>
        Cook
      </BaseButton>
    </div>
    <draggable
      :disabled="!edit"
      :value="value"
      handle=".handle"
      @input="updateIndex"
      @start="drag = true"
      @end="drag = false"
    >
      <div v-for="(step, index) in value" :key="index">
        <v-app-bar v-if="showTitleEditor[index]" class="primary mx-1 mt-6" dark dense rounded>
          <v-toolbar-title v-if="!edit" class="headline">
            <v-app-bar-title v-text="step.title"> </v-app-bar-title>
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
              <v-btn v-if="edit" fab x-small color="white" class="mr-2" elevation="0" @click="value.splice(index, 1)">
                <v-icon size="24" color="error">{{ $globals.icons.delete }}</v-icon>
              </v-btn>

              {{ $t("recipe.step-index", { step: index + 1 }) }}

              <div class="ml-auto">
                <BaseOverflowButton
                  v-if="edit"
                  small
                  mode="event"
                  :items="actionEvents || []"
                  @merge-above="mergeAbove(index - 1, index)"
                  @toggle-section="toggleShowTitle(index)"
                  @link-ingredients="openDialog(index, step.ingredientReferences, step.text)"
                >
                </BaseOverflowButton>
              </div>
              <v-icon v-if="edit" class="handle">{{ $globals.icons.arrowUpDown }}</v-icon>
              <v-fade-transition>
                <v-icon v-show="isChecked(index)" size="24" class="ml-auto" color="success">
                  {{ $globals.icons.checkboxMarkedCircle }}
                </v-icon>
              </v-fade-transition>
            </v-card-title>
            <v-card-text v-if="edit">
              <v-textarea :key="'instructions' + index" v-model="value[index]['text']" auto-grow dense rows="4">
              </v-textarea>
              <div
                v-for="ing in step.ingredientReferences"
                :key="ing.referenceId"
                v-html="getIngredientByRefId(ing.referenceId)"
              />
            </v-card-text>
            <v-expand-transition>
              <div v-show="!isChecked(index) && !edit" class="m-0 p-0">
                <v-card-text>
                  <VueMarkdown :source="step.text"> </VueMarkdown>
                </v-card-text>
              </div>
            </v-expand-transition>
          </v-card>
        </v-hover>
      </div>
    </draggable>
  </section>
</template>

<script lang="ts">
import draggable from "vuedraggable";
// @ts-ignore
import VueMarkdown from "@adapttive/vue-markdown";
import { ref, toRefs, reactive, defineComponent, watch, onMounted } from "@nuxtjs/composition-api";
import { RecipeStep, IngredientToStepRef, RecipeIngredient } from "~/types/api-types/recipe";
import { parseIngredientText } from "~/composables/recipes";

interface MergerHistory {
  target: number;
  source: number;
  targetText: string;
  sourceText: string;
}

export default defineComponent({
  components: {
    VueMarkdown,
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
  },

  setup(props, context) {
    const state = reactive({
      dialog: false,
      disabledSteps: [] as number[],
      unusedIngredients: [] as RecipeIngredient[],
      usedIngredients: [] as RecipeIngredient[],
    });

    const showTitleEditor = ref<boolean[]>([]);

    const actionEvents = [
      {
        text: "Toggle Section",
        event: "toggle-section",
      },
      {
        text: "Link Ingredients",
        event: "link-ingredients",
      },
      {
        text: "Merge Above",
        event: "merge-above",
      },
    ];

    // ===============================================================
    // UI State Helpers
    function validateTitle(title: string | undefined) {
      return !(title === null || title === "");
    }

    watch(props.value, (v) => {
      state.disabledSteps = [];
      showTitleEditor.value = v.map((x) => validateTitle(x.title));
    });

    // Eliminate state with an eager call to watcher?
    onMounted(() => {
      showTitleEditor.value = props.value.map((x) => validateTitle(x.title));
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
    function toggleShowTitle(index: number) {
      const newVal = !showTitleEditor.value[index];
      if (!newVal) {
        props.value[index].title = "";
      }

      // Must create a new temporary list due to vue-composition-api backport limitations (I think...)
      const tempList = [...showTitleEditor.value];
      tempList[index] = newVal;
      showTitleEditor.value = tempList;
    }
    function updateIndex(data: RecipeStep) {
      context.emit("input", data);
    }

    // ===============================================================
    // Ingredient Linker
    const activeRefs = ref<String[]>([]);
    const activeIndex = ref(0);
    const activeText = ref("");

    function openDialog(idx: number, refs: IngredientToStepRef[], text: string) {
      setUsedIngredients();
      activeText.value = text;
      activeIndex.value = idx;
      state.dialog = true;
      activeRefs.value = refs.map((ref) => ref.referenceId);
    }

    function setIngredientIds() {
      const instruction = props.value[activeIndex.value];
      instruction.ingredientReferences = activeRefs.value.map((ref) => {
        return {
          referenceId: ref as string,
        };
      });
      state.dialog = false;
    }

    function setUsedIngredients() {
      const usedRefs: { [key: string]: boolean } = {};

      props.value.forEach((element) => {
        element.ingredientReferences.forEach((ref) => {
          usedRefs[ref.referenceId] = true;
        });
      });

      console.log(usedRefs);

      state.usedIngredients = props.ingredients.filter((ing) => {
        return ing.referenceId in usedRefs;
      });

      state.unusedIngredients = props.ingredients.filter((ing) => {
        return !(ing.referenceId in usedRefs);
      });
    }

    function autoSetReferences() {
      // Ingore matching blacklisted words when auto-linking - This is kind of a cludgey implementation. We're blacklisting common words but
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

          if (searchText.toLowerCase().includes(" " + word) && !activeRefs.value.includes(ingredient.referenceId)) {
            console.info("Word Matched", `'${word}'`, ingredient.note);
            activeRefs.value.push(ingredient.referenceId);
          }
        });
      });
    }

    function getIngredientByRefId(refId: String) {
      const ing = props.ingredients.find((ing) => ing.referenceId === refId) || "";
      if (ing === "") {
        return "";
      }
      return parseIngredientText(ing, props.disableAmount);
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
          title: "",
          text: lastMerge.sourceText,
          ingredientReferences: [],
        });
      }
    }

    return {
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
    };
  },
});
</script>


