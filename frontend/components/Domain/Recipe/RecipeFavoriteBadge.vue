<template>
  <v-tooltip bottom nudge-right="50" :color="buttonStyle ? 'info' : 'secondary'">
    <template #activator="{ on, attrs }">
      <v-btn
        v-if="isFavorite || showAlways"
        small
        :color="buttonStyle ? 'info' : 'secondary'"
        :icon="!buttonStyle"
        :fab="buttonStyle"
        v-bind="attrs"
        @click.prevent="toggleFavorite"
        v-on="on"
      >
        <v-icon :small="!buttonStyle" :color="buttonStyle ? 'white' : 'secondary'">
          {{ isFavorite ? $globals.icons.heart : $globals.icons.heartOutline }}
        </v-icon>
      </v-btn>
    </template>
    <span>{{ isFavorite ? $t("recipe.remove-from-favorites") : $t("recipe.add-to-favorites") }}</span>
  </v-tooltip>
</template>

<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
export default defineComponent({
  props: {
    slug: {
      type: String,
      default: "",
    },
    showAlways: {
      type: Boolean,
      default: false,
    },
    buttonStyle: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const api = useUserApi();
    const { $auth } = useContext();

    // TODO Setup the correct type for $auth.user
    // See https://github.com/nuxt-community/auth-module/issues/1097
    const user = computed(() => $auth.user);
    // @ts-ignore See above
    const isFavorite = computed(() => user.value?.favoriteRecipes?.includes(props.slug));

    async function toggleFavorite() {
      console.log("Favorited?");
      if (!isFavorite.value) {
        // @ts-ignore See above
        await api.users.addFavorite(user.value?.id, props.slug);
      } else {
        // @ts-ignore See above
        await api.users.removeFavorite(user.value?.id, props.slug);
      }
      $auth.fetchUser();
    };

    return { isFavorite, toggleFavorite };
  },
});
</script>

<style lang="scss" scoped>
</style>
