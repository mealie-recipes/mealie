<template>
  <v-container>
    <RecipeCardSection
      v-if="tool"
      :icon="$globals.icons.potSteam"
      :title="tool.name"
      :recipes="recipes"
      :tool-slug="tool.slug"
      @sortRecipes="assignSorted"
      @replaceRecipes="replaceRecipes"
      @appendRecipes="appendRecipes"
      @delete="removeRecipe"
    >
      <template #title>
        <v-btn icon class="mr-1">
          <v-icon dark large @click="reset">
            {{ $globals.icons.potSteam }}
          </v-icon>
        </v-btn>

        <template v-if="edit">
          <v-text-field
            v-model="tool.name"
            autofocus
            single-line
            dense
            hide-details
            class="headline"
            @keyup.enter="updateTools"
          >
          </v-text-field>
          <v-btn icon @click="updateTools">
            <v-icon size="28">
              {{ $globals.icons.save }}
            </v-icon>
          </v-btn>
          <v-btn icon class="mr-1" @click="reset">
            <v-icon size="28">
              {{ $globals.icons.close }}
            </v-icon>
          </v-btn>
        </template>

        <template v-else>
          <v-tooltip top>
            <template #activator="{ on, attrs }">
              <v-toolbar-title v-bind="attrs" style="cursor: pointer" class="headline" v-on="on" @click="edit = true">
                {{ tool.name }}
              </v-toolbar-title>
            </template>
            <span> Click to Edit </span>
          </v-tooltip>
        </template>
      </template>
    </RecipeCardSection>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, useAsync, useRoute, reactive, toRefs, useRouter } from "@nuxtjs/composition-api";
import { useLazyRecipes } from "~/composables/recipes";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useUserApi } from "~/composables/api";

export default defineComponent({
  components: { RecipeCardSection },
  setup() {
    const { recipes, appendRecipes, assignSorted, removeRecipe, replaceRecipes } = useLazyRecipes();

    const api = useUserApi();
    const route = useRoute();
    const router = useRouter();
    const slug = route.value.params.slug;

    const state = reactive({
      initialValue: "",
      edit: false,
    });

    const tool = useAsync(async () => {
      const { data } = await api.tools.bySlug(slug);
      if (data) {
        state.initialValue = data.name;
      }
      return data;
    }, slug);

    function reset() {
      state.edit = false;

      if (tool.value) {
        tool.value.name = state.initialValue;
      }
    }

    async function updateTools() {
      state.edit = false;

      if (!tool.value) {
        return;
      }
      const { data } = await api.tools.updateOne(tool.value.id, tool.value);

      if (data) {
        router.push("/recipes/tools/" + data.slug);
      }
    }

    return {
      tool,
      reset,
      ...toRefs(state),
      updateTools,
      appendRecipes,
      assignSorted,
      recipes,
      removeRecipe,
      replaceRecipes,
    };
  },
  head() {
    return {
      title: this.$t("tool.tools") as string,
    };
  },
});
</script>
