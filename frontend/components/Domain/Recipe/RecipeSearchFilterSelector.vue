<template>
  <v-toolbar dense flat>
    <v-btn-toggle v-model="selected" tile group color="primary accent-3" mandatory @change="emitMulti">
      <v-btn small :value="false">
        {{ $t("search.include") }}
      </v-btn>

      <v-btn small :value="true">
        {{ $t("search.exclude") }}
      </v-btn>
    </v-btn-toggle>
    <v-spacer></v-spacer>
    <v-btn-toggle v-model="match" tile group color="primary accent-3" mandatory @change="emitMulti">
      <v-btn small :value="false" class="text-uppercase">
        {{ $t("search.and") }}
      </v-btn>
      <v-btn small :value="true" class="text-uppercase">
        {{ $t("search.or") }}
      </v-btn>
    </v-btn-toggle>
  </v-toolbar>
</template>

<script lang="ts">
import { defineComponent } from "vue-demi";

type SelectionValue = "include" | "exclude" | "any";

export default defineComponent({
  props: {
    value: {
      type: String as () => SelectionValue,
      default: "include",
    },
  },
  data() {
    return {
      selected: false,
      match: false,
    };
  },
  methods: {
    emitChange() {
      this.$emit("input", this.selected);
    },
    emitMulti() {
      const updateData = {
        exclude: this.selected,
        matchAny: this.match,
      };
      this.$emit("update", updateData);
    },
  },
});
</script>

<style lang="scss" scoped></style>
