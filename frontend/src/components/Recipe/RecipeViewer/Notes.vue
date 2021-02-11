<template>
  <div>
    <h2 v-if="notes[0]" class="my-4">{{ $t("recipe.notes") }}</h2>
    <v-card
      class="mt-1"
      v-for="(note, index) in notes"
      :key="generateKey('note', index)"
    >
      <v-card-title> {{ note.title }}</v-card-title>
      <v-card-text>
        <vue-markdown :source="note.text"> </vue-markdown>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import VueMarkdown from "@adapttive/vue-markdown";
import utils from "@/utils";
export default {
  props: {
    notes: Array,
  },
  components: {
    VueMarkdown,
  },
  methods: {
    generateKey(item, index) {
      return utils.generateUniqueKey(item, index);
    },
  },
};
</script>

<style>
</style>