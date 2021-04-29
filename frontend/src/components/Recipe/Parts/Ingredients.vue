<template>
  <div>
    <h2 class="mb-4">{{ $t("recipe.ingredients") }}</h2>
    <div v-if="edit">
      <draggable
        :value="value"
        @input="updateIndex"
        @start="drag = true"
        @end="drag = false"
        handle=".handle"
      >
        <transition-group type="transition" :name="!drag ? 'flip-list' : null">
          <div
            v-for="(ingredient, index) in value"
            :key="generateKey('ingredient', index)"
          >
            <v-row align="center">
              <v-textarea
                class="mr-2"
                :label="$t('recipe.ingredient')"
                v-model="value[index]"
                mdi-move-resize
                auto-grow
                solo
                dense
                rows="1"
              >
                <template slot="append-outer">
                  <v-icon class="handle">mdi-arrow-up-down</v-icon>
                </template>
                <v-icon
                  class="mr-n1"
                  slot="prepend"
                  color="error"
                  @click="removeByIndex(value, index)"
                >
                  mdi-delete
                </v-icon>
              </v-textarea>
            </v-row>
          </div>
        </transition-group>
      </draggable>

      <div class="d-flex row justify-end">
        <BulkAdd @bulk-data="addIngredient" class="mr-2" />
        <v-btn color="secondary" dark @click="addIngredient" class="mr-4">
          <v-icon>mdi-plus</v-icon>
        </v-btn>
      </div>
    </div>
    <div v-else>
      <v-list-item
        dense
        v-for="(ingredient, index) in value"
        :key="generateKey('ingredient', index)"
        @click="toggleChecked(index)"
      >
        <v-checkbox
          hide-details
          :value="checked[index]"
          class="pt-0 my-auto py-auto"
          color="secondary"
        >
        </v-checkbox>

        <v-list-item-content>
          <vue-markdown
            class="ma-0 pa-0 text-subtitle-1 dense-markdown"
            :source="ingredient"
          >
          </vue-markdown>
        </v-list-item-content>
      </v-list-item>
    </div>
  </div>
</template>

<script>
import BulkAdd from "@/components/Recipe/Parts/Helpers/BulkAdd";
import VueMarkdown from "@adapttive/vue-markdown";
import draggable from "vuedraggable";
import utils from "@/utils";
export default {
  components: {
    BulkAdd,
    draggable,
    VueMarkdown,
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
      drag: false,
      checked: [],
    };
  },
  mounted() {
    this.checked = this.value.map(() => false);
  },
  methods: {
    addIngredient(ingredients = null) {
      if (ingredients.length) {
        this.value.push(...ingredients);
      } else {
        this.value.push("");
      }
    },
    generateKey(item, index) {
      return utils.generateUniqueKey(item, index);
    },
    updateIndex(data) {
      this.$emit("input", data);
    },
    toggleChecked(index) {
      this.$set(this.checked, index, !this.checked[index]);
    },
    removeByIndex(list, index) {
      list.splice(index, 1);
    },
  },
};
</script>

<style >
.dense-markdown p {
  margin: auto !important;
}
</style>