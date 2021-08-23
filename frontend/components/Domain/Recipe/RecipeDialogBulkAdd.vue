<template>
  <div class="text-center">
    <v-dialog v-model="dialog" width="600">
      <template #activator="{ on, attrs }">
        <BaseButton v-bind="attrs" v-on="on" @click="inputText = ''">
          {{ $t("new-recipe.bulk-add") }}
        </BaseButton>
      </template>

      <v-card>
        <v-card-title class="headline"> {{ $t("new-recipe.bulk-add") }} </v-card-title>

        <v-card-text>
          <p>
            {{ $t("new-recipe.paste-in-your-recipe-data-each-line-will-be-treated-as-an-item-in-a-list") }}
          </p>
          <v-textarea v-model="inputText"> </v-textarea>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="success" text @click="save"> {{ $t("general.save") }} </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  data() {
    return {
      dialog: false,
      inputText: "",
    };
  },
  methods: {
    splitText() {
      const split = this.inputText.split("\n");

      split.forEach((element, index) => {
        if ((element === "\n") | (element === false)) {
          split.splice(index, 1);
        }
      });

      return split;
    },
    save() {
      this.$emit("bulk-data", this.splitText());
      this.dialog = false;
    },
  },
};
</script>
