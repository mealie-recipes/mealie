<template>
  <div v-if="value.length > 0 || edit" class="mt-8">
    <h2 class="my-4">{{ $t("recipe.note") }}</h2>
    <div v-for="(note, index) in value" :key="'note' + index" class="mt-1">
      <v-card v-if="edit">
        <v-card-text>
          <div class="d-flex align-center">
            <v-text-field v-model="value[index]['title']" :label="$t('recipe.title')" />
            <v-btn icon class="mr-2" elevation="0" @click="removeByIndex(value, index)">
              <v-icon>{{ $globals.icons.delete }}</v-icon>
            </v-btn>
          </div>
          <v-textarea v-model="value[index]['text']" auto-grow :placeholder="$t('recipe.note')" />
        </v-card-text>
      </v-card>
      <div v-else>
        <v-card-title class="text-subtitle-1 font-weight-medium py-1">
          {{ note.title }}
        </v-card-title>
        <v-card-text>
          <VueMarkdown :source="note.text"> </VueMarkdown>
        </v-card-text>
      </div>
    </div>

    <div v-if="edit" class="d-flex justify-end">
      <BaseButton class="ml-auto my-2" @click="addNote"> {{ $t("general.new") }}</BaseButton>
    </div>
  </div>
</template>

<script lang="ts">
// @ts-ignore vue-markdown has no types
import VueMarkdown from "@adapttive/vue-markdown";
import { defineComponent } from "@nuxtjs/composition-api";
import { RecipeNote } from "~/types/api-types/recipe";

export default defineComponent({
  components: {
    VueMarkdown,
  },
  props: {
    value: {
      type: Array as () => RecipeNote[],
      required: true,
    },

    edit: {
      type: Boolean,
      default: true,
    },
  },
  setup(props) {
    function addNote() {
      props.value.push({ title: "", text: "" });
    }

    function removeByIndex(list: unknown[], index: number) {
      list.splice(index, 1);
    }

    return {
      addNote,
      removeByIndex,
    };
  },
});
</script>

<style></style>
