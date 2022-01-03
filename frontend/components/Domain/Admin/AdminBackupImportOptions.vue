<template>
  <div>
    <v-checkbox
      v-for="(option, index) in options"
      :key="index"
      v-model="option.value"
      class="mb-n4 mt-n3"
      dense
      :label="option.text"
      @change="emitValue()"
    ></v-checkbox>
    <template v-if="importBackup">
      <v-divider class="my-3"></v-divider>
      <v-checkbox
        v-model="forceImport"
        class="mb-n4"
        dense
        :label="$t('settings.remove-existing-entries-matching-imported-entries')"
        @change="emitValue()"
      ></v-checkbox>
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, useContext } from "@nuxtjs/composition-api";

const UPDATE_EVENT = "input";
export default defineComponent({
  props: {
    importBackup: {
      type: Boolean,
      default: false,
    },
  },
  setup(_, context) {
    const { i18n } = useContext();

    const options = {
      recipes: {
        value: true,
        text: i18n.t("general.recipes"),
      },
      users: {
        value: true,
        text: i18n.t("user.users"),
      },
      groups: {
        value: true,
        text: i18n.t("group.groups"),
      },
    }
    const forceImport = false;

    function emitValue() {
      context.emit(UPDATE_EVENT, {
        recipes: options.recipes.value,
        settings: false,
        themes: false,
        pages: false,
        users: options.users.value,
        groups: options.groups.value,
        notifications: false,
        forceImport,
      });
    }

    onMounted(() => {
      emitValue();
    });

    return {
      options,
      forceImport,
      emitValue,
    };
  },
});
</script>
