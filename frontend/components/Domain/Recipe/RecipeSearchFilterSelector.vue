<template>
  <div class="d-flex justify-center align-center">
    <v-btn-toggle v-model="selected" tile group color="primary accent-3" mandatory="force" @change="emitMulti">
      <v-btn size="small" :value="false">
        {{ $t("search.include") }}
      </v-btn>
      <v-btn size="small" :value="true">
        {{ $t("search.exclude") }}
      </v-btn>
    </v-btn-toggle>
    <v-btn-toggle v-model="match" tile group color="primary accent-3" mandatory="force" @change="emitMulti">
      <v-btn size="small" :value="false" class="text-uppercase">
        {{ $t("search.and") }}
      </v-btn>
      <v-btn size="small" :value="true" class="text-uppercase">
        {{ $t("search.or") }}
      </v-btn>
    </v-btn-toggle>
  </div>
</template>

<script lang="ts">
type SelectionValue = "include" | "exclude" | "any";

export default defineNuxtComponent({
  props: {
    modelValue: {
      type: String as () => SelectionValue,
      default: "include",
    },
  },
  emits: ["update:modelValue", "update"],
  data() {
    return {
      selected: false,
      match: false,
    };
  },
  methods: {
    emitChange() {
      this.$emit("update:modelValue", this.selected);
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
