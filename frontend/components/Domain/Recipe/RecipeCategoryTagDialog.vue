<template>
  <div>
    <slot>
      <v-btn icon class="mt-n1" @click="dialog = true">
        <v-icon :color="color">{{ $globals.icons.create }}</v-icon>
      </v-btn>
    </slot>
    <v-dialog v-model="dialog" width="500">
      <v-card>
        <v-app-bar dense dark color="primary mb-2">
          <v-icon large left class="mt-1">
            {{ $globals.icons.tags }}
          </v-icon>

          <v-toolbar-title class="headline">
            {{ title }}
          </v-toolbar-title>

          <v-spacer></v-spacer>
        </v-app-bar>
        <v-card-title> </v-card-title>
        <v-form @submit.prevent="select">
          <v-card-text>
            <v-text-field v-model="itemName" dense :label="inputLabel" :rules="[rules.required]"></v-text-field>
          </v-card-text>
          <v-card-actions>
            <BaseButton cancel @click="dialog = false" />
            <v-spacer></v-spacer>
            <BaseButton type="submit" create :disabled="!itemName" />
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { defineComponent } from "@nuxtjs/composition-api";
import { useApiSingleton } from "~/composables/use-api";
const CREATED_ITEM_EVENT = "created-item";
export default defineComponent({
  props: {
    buttonText: {
      type: String,
      default: "Add",
    },
    value: {
      type: String,
      default: "",
    },
    color: {
      type: String,
      default: null,
    },
    tagDialog: {
      type: Boolean,
      default: true,
    },
  },
  setup() {
    const api = useApiSingleton();

    return { api };
  },
  data() {
    return {
      dialog: false,
      itemName: "",
      rules: {
        required: (val) => !!val || "A Name is Required",
      },
    };
  },

  computed: {
    title() {
      return this.tagDialog ? "Create a Tag" : "Create a Category";
    },
    inputLabel() {
      return this.tagDialog ? "Tag Name" : "Category Name";
    },
  },
  watch: {
    dialog(val) {
      if (!val) this.itemName = "";
    },
  },

  methods: {
    open() {
      this.dialog = true;
    },
    async select() {
      const newItem = await (async () => {
        if (this.tagDialog) {
          const newItem = await this.api.tags.createOne({ name: this.itemName });
          return newItem;
        } else {
          const newItem = await this.api.categories.createOne({ name: this.itemName });
          return newItem;
        }
      })();

      this.$emit(CREATED_ITEM_EVENT, newItem);
      this.dialog = false;
    },
  },
});
</script>

<style></style>
