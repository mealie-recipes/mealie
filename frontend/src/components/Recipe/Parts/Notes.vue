<template>
  <div v-if="value.length > 0 || edit">
    <h2 class="my-4">{{ $t("recipe.note") }}</h2>
    <v-card class="mt-1" v-for="(note, index) in value" :key="generateKey('note', index)">
      <div v-if="edit">
        <v-card-text>
          <v-row align="center">
            <v-btn fab x-small color="white" class="mr-2" elevation="0" @click="removeByIndex(value, index)">
              <v-icon color="error">mdi-delete</v-icon>
            </v-btn>
            <v-text-field :label="$t('recipe.title')" v-model="value[index]['title']"></v-text-field>
          </v-row>

          <v-textarea auto-grow :placeholder="$t('recipe.note')" v-model="value[index]['text']"> </v-textarea>
        </v-card-text>
      </div>
      <div v-else>
        <v-card-title class="py-2">
          {{ note.title }}
        </v-card-title>
        <v-divider class="mx-2"></v-divider>
        <v-card-text>
          <vue-markdown :source="note.text"> </vue-markdown>
        </v-card-text>
      </div>
    </v-card>

    <div class="d-flex justify-end" v-if="edit">
      <v-btn class="mt-1" color="secondary" dark @click="addNote">
        <v-icon>mdi-plus</v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script>
import VueMarkdown from "@adapttive/vue-markdown";
import { utils } from "@/utils";
export default {
  components: {
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
  methods: {
    generateKey(item, index) {
      return utils.generateUniqueKey(item, index);
    },
    addNote() {
      this.value.push({ text: "" });
    },
    removeByIndex(list, index) {
      list.splice(index, 1);
    },
  },
};
</script>

<style></style>
