<template>
  <v-toolbar dense flat>
    <v-btn-toggle tile group v-model="selected" color="primary accent-3" @change="emitMulti" mandatory>
      <v-btn small :value="false">
        {{ $t("search.include") }}
      </v-btn>

      <v-btn small :value="true">
        {{ $t("search.exclude") }}
      </v-btn>
    </v-btn-toggle>
    <v-spacer></v-spacer>
    <v-btn-toggle tile group v-model="match" color="primary accent-3" @change="emitMulti" mandatory>
      <v-btn small :value="false">
        {{ $t("search.and") }}
      </v-btn>
      <v-btn small :value="true">
        {{ $t("search.or") }}
      </v-btn>
    </v-btn-toggle>
  </v-toolbar>
</template>

<script>
export default {
  props: {
    value: {
      default: "include", // Optionas: "include", "exclude", "any"
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
};
</script>

<style lang="scss" scoped></style>
