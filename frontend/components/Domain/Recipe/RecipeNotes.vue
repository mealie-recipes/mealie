<template>
  <div v-if="value.length > 0 || edit">
    <h2 class="my-4">{{ $t("recipe.note") }}</h2>
    <v-card v-for="(note, index) in value" :key="'note' + index" class="mt-1">
      <div v-if="edit">
        <v-card-text>
          <v-row align="center">
            <v-btn fab x-small color="white" class="mr-2" elevation="0" @click="removeByIndex(value, index)">
              <v-icon color="error">{{ $globals.icons.delete }}</v-icon>
            </v-btn>
            <v-text-field v-model="value[index]['title']" :label="$t('recipe.title')"></v-text-field>
          </v-row>

          <v-textarea v-model="value[index]['text']" auto-grow :placeholder="$t('recipe.note')"> </v-textarea>
        </v-card-text>
      </div>
      <div v-else>
        <v-card-title class="py-2">
          {{ note.title }}
        </v-card-title>
        <v-divider class="mx-2"></v-divider>
        <v-card-text>
          <VueMarkdown :source="note.text"> </VueMarkdown>
        </v-card-text>
      </div>
    </v-card>

    <div v-if="edit" class="d-flex justify-end">
      <v-btn class="mt-1" color="secondary" dark @click="addNote">
        <v-icon>{{ $globals.icons.create }}</v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script>
import VueMarkdown from "@adapttive/vue-markdown";
export default {
  components: {
    VueMarkdown,
  },
  props: {
    value: {
      type: Array,
      required: true,
    },

    edit: {
      type: Boolean,
      default: true,
    },
  },
  methods: {
    addNote() {
      this.value.push({ title: "", text: "" });
    },
    removeByIndex(list, index) {
      list.splice(index, 1);
    },
  },
};
</script>

<style></style>
