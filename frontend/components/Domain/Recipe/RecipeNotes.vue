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
      <BaseButton class="ml-auto my-2" @click="addNote"> {{ $t("general.new") }}</BaseButton>
    </div>
  </div>
</template>

<script lang="ts">
// @ts-ignore
import VueMarkdown from "@adapttive/vue-markdown";
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
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
