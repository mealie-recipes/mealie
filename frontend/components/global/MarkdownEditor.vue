<template>
  <div>
    <v-tabs v-model="tab" height="30px" class="my-1">
      <v-tab>
        <v-icon small left> {{ $globals.icons.edit }}</v-icon>
        Edit
      </v-tab>
      <v-tab>
        <v-icon small left> {{ $globals.icons.eye }}</v-icon>
        Preview
      </v-tab>
    </v-tabs>
    <v-textarea
      v-if="tab == 0"
      v-model="inputVal"
      :class="label == '' ? '' : 'mt-5'"
      :label="label"
      auto-grow
      dense
      rows="4"
    ></v-textarea>
    <VueMarkdown v-else :source="value"> </VueMarkdown>
  </div>
</template>

<script lang="ts">
// @ts-ignore
import VueMarkdown from "@adapttive/vue-markdown";

import { defineComponent, reactive, toRefs, computed } from "@nuxtjs/composition-api";

export default defineComponent({
  name: "MarkdownEditor",
  components: {
    VueMarkdown,
  },
  props: {
    value: {
      type: String,
      required: true,
    },
    label: {
      type: String,
      default: "",
    },
  },
  setup(props, context) {
    const state = reactive({
      tab: 0,
    });

    const inputVal = computed({
      get: () => {
        return props.value;
      },
      set: (val) => {
        context.emit("input", val);
      },
    });
    return {
      inputVal,
      ...toRefs(state),
    };
  },
});
</script>

