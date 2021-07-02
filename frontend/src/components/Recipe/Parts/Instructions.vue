<template>
  <div>
    <h2 class="mb-4">{{ $t("recipe.instructions") }}</h2>
    <div>
      <draggable
        :disabled="!edit"
        :value="value"
        @input="updateIndex"
        @start="drag = true"
        @end="drag = false"
        handle=".handle"
      >
        <div v-for="(step, index) in value" :key="index">
          <v-app-bar v-if="showTitleEditor[index]" class="primary mx-1 mt-6" dark dense rounded>
            <v-toolbar-title class="headline" v-if="!edit">
              <v-app-bar-title v-text="step.title"> </v-app-bar-title>
            </v-toolbar-title>
            <v-text-field
              v-if="edit"
              class="headline pa-0 mt-5"
              v-model="step.title"
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
              :ripple="!edit"
              @click="toggleDisabled(index)"
            >
              <v-card-title :class="{ 'pb-0': !isChecked(index) }">
                <v-btn
                  v-if="edit"
                  fab
                  x-small
                  color="white"
                  class="mr-2"
                  elevation="0"
                  @click="removeByIndex(value, index)"
                >
                  <v-icon size="24" color="error">{{ $globals.icons.delete }}</v-icon>
                </v-btn>

                {{ $t("recipe.step-index", { step: index + 1 }) }}

                <v-fade-transition>
                  <v-icon v-if="isChecked(index)" size="24" class="ml-auto" color="success">
                    {{ $globals.icons.checkboxMarkedCircle }}
                  </v-icon>
                </v-fade-transition>

                <v-btn v-if="edit" text color="primary" class="ml-auto" @click="toggleShowTitle(index)">
                  {{ !showTitleEditor[index] ? $t("recipe.insert-section") : $t("recipe.remove-section") }}
                </v-btn>
                <v-icon v-if="edit" class="handle">{{ $globals.icons.arrowUpDown }}</v-icon>
              </v-card-title>
              <v-card-text v-if="edit">
                <v-textarea
                  auto-grow
                  dense
                  v-model="value[index]['text']"
                  :key="generateKey('instructions', index)"
                  rows="4"
                >
                </v-textarea>
              </v-card-text>
              <v-expand-transition>
                <div class="m-0 p-0" v-if="!isChecked(index) && !edit">
                  <v-card-text>
                    <vue-markdown :source="step.text"> </vue-markdown>
                  </v-card-text>
                </div>
              </v-expand-transition>
            </v-card>
          </v-hover>
        </div>
      </draggable>
    </div>
  </div>
</template>

<script>
import draggable from "vuedraggable";
import VueMarkdown from "@adapttive/vue-markdown";
import { utils } from "@/utils";
export default {
  components: {
    VueMarkdown,
    draggable,
  },
  props: {
    value: {
      type: Array,
    },

    edit: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      disabledSteps: [],
      showTitleEditor: [],
    };
  },

  mounted() {
    this.showTitleEditor = this.value.map(x => this.validateTitle(x.title));
  },

  watch: {
    value: {
      handler() {
        this.disabledSteps = [];
      },
    },
  },

  methods: {
    generateKey(item, index) {
      return utils.generateUniqueKey(item, index);
    },
    removeByIndex(list, index) {
      list.splice(index, 1);
    },
    validateTitle(title) {
      return !(title === null || title === "");
    },
    toggleDisabled(stepIndex) {
      if (this.edit) return;
      if (this.disabledSteps.includes(stepIndex)) {
        let index = this.disabledSteps.indexOf(stepIndex);
        if (index !== -1) {
          this.disabledSteps.splice(index, 1);
        }
      } else {
        this.disabledSteps.push(stepIndex);
      }
    },
    isChecked(stepIndex) {
      if (this.disabledSteps.includes(stepIndex) && !this.edit) {
        return "disabled-card";
      } else {
        return;
      }
    },
    toggleShowTitle(index) {
      const newVal = !this.showTitleEditor[index];
      if (!newVal) {
        this.value[index].title = "";
      }
      this.$set(this.showTitleEditor, index, newVal);
    },
    updateIndex(data) {
      this.$emit("input", data);
    },
  },
};
</script>


