<template>
  <div>
    <v-checkbox
      v-for="option in options"
      :key="option.text"
      class="mb-n4 mt-n3"
      dense
      :label="option.text"
      v-model="option.value"
      @change="emitValue()"
    ></v-checkbox>
  </div>
</template>

<script>
const UPDATE_EVENT = "update-options";
export default {
  data() {
    return {
      options: {
        recipes: {
          value: true,
          text: this.$t("general.recipes"),
        },
        settings: {
          value: true,
          text: this.$t("general.settings"),
        },
        pages: {
          value: true,
          text: this.$t("settings.pages"),
        },
        themes: {
          value: true,
          text: this.$t("general.themes"),
        },
        users: {
          value: true,
          text: this.$t("general.users"),
        },
        groups: {
          value: true,
          text: this.$t("general.groups"),
        },
      },
    };
  },
  mounted() {
    this.emitValue();
  },
  methods: {
    emitValue() {
      this.$emit(UPDATE_EVENT, {
        recipes: this.options.recipes.value,
        settings: this.options.settings.value,
        themes: this.options.themes.value,
        pages: this.options.pages.value,
        users: this.options.users.value,
        groups: this.options.groups.value,
      });
    },
  },
};
</script>

<style lang="scss" scoped>
</style>