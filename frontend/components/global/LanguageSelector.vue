<template>
<v-select
  v-model="locale"
  :items="locales"
  item-text="code"
  menu-props="auto"
  hide-details
  dense
></v-select>
</template>

<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
import type { LocaleObject } from "@nuxtjs/i18n";

export default defineComponent({
  setup() {
    const { i18n } = useContext();

    const locales = computed(() => (i18n.locales as LocaleObject[]).sort((a, b) => a.code.localeCompare(b.code)));

    const locale = computed<string>({
      get() {
        return i18n.locale;
      },
      set(value) {
        i18n.setLocale(value);
        // Reload the page to update the language - not all strings are reactive
        window.location.reload();
      }
    });

    return {
      i18n,
      locales,
      locale,
    };
  }
});
</script>

<style scoped>

</style>
