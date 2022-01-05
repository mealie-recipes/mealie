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
            <v-text-field
              v-model="itemName"
              dense
              :label="inputLabel"
              :rules="[rules.required]"
              autofocus
            ></v-text-field>
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

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";

const CREATED_ITEM_EVENT = "created-item";

export default defineComponent({
  props: {
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
  setup(props, context) {
    const title = computed(() => props.tagDialog ? "Create a Tag" : "Create a Category");
    const inputLabel = computed(() => props.tagDialog ? "Tag Name" : "Category Name");

    const rules = {
        required: (val: string) => !!val || "A Name is Required",
      };

    const state = reactive({
      dialog: false,
      itemName: "",
    });

    watch(() => state.dialog, (val: boolean) => {
      if (!val) state.itemName = "";
    });

    const api = useUserApi();
    async function select() {
      const newItem = await (async () => {
        if (props.tagDialog) {
          const { data } = await api.tags.createOne({ name: state.itemName });
          return data;
        } else {
          const { data } = await api.categories.createOne({ name: state.itemName });
          return data;
        }
      })();

      console.log(newItem);

      context.emit(CREATED_ITEM_EVENT, newItem);
      state.dialog = false;
    }


    return {
      ...toRefs(state),
      title,
      inputLabel,
      rules,
      select,
    };
  },
});
</script>

<style></style>
