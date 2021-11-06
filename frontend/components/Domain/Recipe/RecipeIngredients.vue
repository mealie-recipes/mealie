<template>
  <div v-if="value && value.length > 0">
    <div class="d-flex justify-start">
      <h2 class="mb-4 mt-1">{{ $t("recipe.ingredients") }}</h2>
    <AppButtonCopy btn-class="ml-auto" :copy-text="ingredientCopyText" />
    </div>
    <div>
      <div v-for="(ingredient, index) in value" :key="'ingredient' + index">
        <h3 v-if="showTitleEditor[index]" class="mt-2">{{ ingredient.title }}</h3>
        <v-divider v-if="showTitleEditor[index]"></v-divider>
        <v-list-item dense @click="toggleChecked(index)">
          <v-checkbox hide-details :value="checked[index]" class="pt-0 my-auto py-auto" color="secondary"> </v-checkbox>
          <v-list-item-content>
            <VueMarkdown
              class="ma-0 pa-0 text-subtitle-1 dense-markdown"
              :source="parseIngredientText(ingredient, disableAmount, scale)"
            >
            </VueMarkdown>
          </v-list-item-content>
        </v-list-item>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, defineComponent } from "@nuxtjs/composition-api";
import VueMarkdown from "@adapttive/vue-markdown";
import { parseIngredientText } from "~/composables/recipes";
export default defineComponent({
  components: {
    VueMarkdown,
  },
  props: {
    value: {
      type: Array,
      default: () => [],
    },
    disableAmount: {
      type: Boolean,
      default: false,
    },
    scale: {
      type: Number,
      default: 1,
    },
  },
  setup(props) {
    const ingredientCopyText = computed(() => {
      return props.value
        .map((ingredient) => {
          return `- [ ] ${parseIngredientText(ingredient, props.disableAmount, props.scale)}`;
        })
        .join("\n");
    });

    return { parseIngredientText, ingredientCopyText };
  },
  data() {
    return {
      drag: false,
      checked: [],
      showTitleEditor: [],
    };
  },
  watch: {
    value: {
      handler() {
        this.showTitleEditor = this.value.map((x) => this.validateTitle(x.title));
      },
    },
  },
  mounted() {
    this.checked = this.value.map(() => false);
    this.showTitleEditor = this.value.map((x) => this.validateTitle(x.title));
  },
  methods: {
    toggleChecked(index) {
      this.$set(this.checked, index, !this.checked[index]);
    },

    validateTitle(title) {
      return !(title === null || title === "");
    },
    toggleShowTitle(index) {
      const newVal = !this.showTitleEditor[index];
      if (!newVal) {
        this.value[index].title = "";
      }
      this.$set(this.showTitleEditor, index, newVal);
    },
  },
});
</script>

<style>
.dense-markdown p {
  margin: auto !important;
}
</style>
