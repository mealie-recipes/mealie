<template>
  <div class="text-center">
    <v-dialog v-model="dialog" width="800">
      <template #activator="{ on, attrs }">
        <BaseButton v-bind="attrs" v-on="on" @click="inputText = ''">
          {{ $t("new-recipe.bulk-add") }}
        </BaseButton>
      </template>

      <v-card>
        <v-app-bar dark color="primary" class="mt-n1 mb-3">
          <v-icon large left>
            {{ $globals.icons.createAlt }}
          </v-icon>
          <v-toolbar-title class="headline"> {{ $t("new-recipe.bulk-add") }}</v-toolbar-title>
          <v-spacer></v-spacer>
        </v-app-bar>

        <v-card-text>
          <v-textarea
            v-model="inputText"
            outlined
            rows="12"
            :placeholder="$t('new-recipe.paste-in-your-recipe-data-each-line-will-be-treated-as-an-item-in-a-list')"
          >
          </v-textarea>
          <v-tooltip top>
            <template #activator="{ on, attrs }">
              <v-btn outlined color="info" small v-bind="attrs" @click="trimAllLines" v-on="on">
                Trim Whitespace
              </v-btn>
            </template>
            <span> Trim leading and trailing whitespace as well as blank lines </span>
          </v-tooltip>

          <v-tooltip top>
            <template #activator="{ on, attrs }">
              <v-btn class="ml-1" outlined color="info" small v-bind="attrs" @click="removeFirstCharacter" v-on="on">
                Trim Prefix
              </v-btn>
            </template>
            <span> Trim first character from each line </span>
          </v-tooltip>
          <v-tooltip top>
            <template #activator="{ on, attrs }">
              <v-btn class="ml-1" outlined color="info" small v-bind="attrs" @click="splitByNumberedLine" v-on="on">
                Split By Numbered Line
              </v-btn>
            </template>
            <span> Attempts to split a paragraph by matching 1) or 1. patterns </span>
          </v-tooltip>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <BaseButton cancel @click="dialog = false"> </BaseButton>
          <v-spacer></v-spacer>
          <BaseButton save color="success" @click="save"> </BaseButton>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { reactive, toRefs, defineComponent } from "@nuxtjs/composition-api";
export default defineComponent({
  setup(_, context) {
    const state = reactive({
      dialog: false,
      inputText: "",
    });

    function splitText() {
      return state.inputText.split("\n").filter((line) => !(line === "\n" || !line));
    }

    function removeFirstCharacter() {
      state.inputText = splitText()
        .map((line) => line.substr(1))
        .join("\n");
    }

    const numberedLineRegex = /\d+[.):] /gm;

    function splitByNumberedLine() {
      // Split inputText by numberedLineRegex
      const matches = state.inputText.match(numberedLineRegex);

      matches?.forEach((match, idx) => {
        const replaceText = idx === 0 ? "" : "\n";
        state.inputText = state.inputText.replace(match, replaceText);
      });
    }

    function trimAllLines() {
      const splitLines = splitText();

      splitLines.forEach((element: string, index: number) => {
        splitLines[index] = element.trim();
      });

      state.inputText = splitLines.join("\n");
    }

    function save() {
      context.emit("bulk-data", splitText());
      state.dialog = false;
    }

    return {
      splitText,
      trimAllLines,
      removeFirstCharacter,
      splitByNumberedLine,
      save,
      ...toRefs(state),
    };
  },
});
</script>
