<template>
  <div class="text-center">
    <v-dialog v-model="dialog" width="600">
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
          <p>
            {{ $t("new-recipe.paste-in-your-recipe-data-each-line-will-be-treated-as-an-item-in-a-list") }}
          </p>
          <v-textarea v-model="inputText" outlined rows="10"> </v-textarea>
          <v-btn outlined color="info" small @click="trimAllLines"> Trim Whitespace </v-btn>
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
import { reactive, toRefs } from "@nuxtjs/composition-api";
export default {
  setup(_, context) {
    const state = reactive({
      dialog: false,
      inputText: "",
    });

    function splitText() {
      return state.inputText.split("\n").filter((line) => !(line === "\n" || !line));
    }

    function trimAllLines() {
      const splitLintes = splitText();

      splitLintes.forEach((element: string, index: number) => {
        splitLintes[index] = element.trim();
      });

      state.inputText = splitLintes.join("\n");
    }

    function save() {
      context.emit("bulk-data", splitText());
      state.dialog = false;
    }

    return {
      splitText,
      trimAllLines,
      save,
      ...toRefs(state),
    };
  },
};
</script>
