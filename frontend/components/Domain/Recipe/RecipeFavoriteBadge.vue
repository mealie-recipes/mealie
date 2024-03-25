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
import { useUserSelfRatings } from "~/composables/use-users";
import { useUserApi } from "~/composables/api";
import { UserOut } from "~/lib/api/types/user";
export default defineComponent({
  props: {
    recipeId: {
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
    const { userRatings, refreshUserRatings } = useUserSelfRatings();

    // TODO Setup the correct type for $auth.user
    // See https://github.com/nuxt-community/auth-module/issues/1097
    const user = computed(() => $auth.user as unknown as UserOut);
    const isFavorite = computed(() => {
      const rating = userRatings.value.find((r) => r.recipeId === props.recipeId);
      return rating?.isFavorite || false;
    });

    async function toggleFavorite() {
      if (!isFavorite.value) {
        await api.users.addFavorite(user.value?.id, props.recipeId);
      } else {
        await api.users.removeFavorite(user.value?.id, props.recipeId);
      }
      await refreshUserRatings();
    }

    return { isFavorite, toggleFavorite };
  },
});
</script>
