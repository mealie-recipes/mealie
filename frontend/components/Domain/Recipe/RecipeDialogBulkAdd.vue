<template>
  <div class="text-center">
    <v-dialog v-model="dialog" width="800">
      <template #activator="{ on, attrs }">
        <BaseButton v-bind="attrs" v-on="on" @click="inputText = ''">
          {{ $t("new-recipe.bulk-add") }}
        </BaseButton>
      </template>

      <v-card>
        <v-app-bar dense dark color="primary" class="mb-2">
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
            hide-details
            :placeholder="$t('new-recipe.paste-in-your-recipe-data-each-line-will-be-treated-as-an-item-in-a-list')"
          >
          </v-textarea>

          <v-divider></v-divider>
          <template v-for="(util, idx) in utilities">
            <v-list-item :key="util.id" dense class="py-1">
              <v-list-item-title>
                <v-list-item-subtitle class="wrap-word">
                  {{ util.description }}
                </v-list-item-subtitle>
              </v-list-item-title>
              <BaseButton small color="info" @click="util.action">
                <template #icon> {{ $globals.icons.robot }}</template>
                Run
              </BaseButton>
            </v-list-item>
            <v-divider :key="`divider-${idx}`" class="mx-2"></v-divider>
          </template>
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
import { reactive, toRefs, defineComponent, useContext } from "@nuxtjs/composition-api";
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
        .map((line) => line.substring(1))
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

    const { i18n } = useContext();

    const utilities = [
      {
        id: "trim-whitespace",
        description: i18n.tc("new-recipe.trim-whitespace-description"),
        action: trimAllLines,
      },
      {
        id: "trim-prefix",
        description: i18n.tc("new-recipe.trim-prefix-description"),
        action: removeFirstCharacter,
      },
      {
        id: "split-by-numbered-line",
        description: i18n.tc("new-recipe.split-by-numbered-line-description"),
        action: splitByNumberedLine,
      },
    ];

    return {
      utilities,
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
