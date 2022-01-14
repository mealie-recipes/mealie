<template>
  <v-container>
    <RecipeCardSection v-if="tools" :title="tools.name" :recipes="tools.recipes" @sort="assignSorted">
      <template #title>
        <v-btn icon class="mr-1">
          <v-icon dark large @click="reset">
            {{ $globals.icons.potSteam }}
          </v-icon>
        </v-btn>

        <template v-if="edit">
          <v-text-field
            v-model="tools.name"
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
                {{ tools.name }}
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
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useUserApi } from "~/composables/api";
import { Recipe } from "~/types/api-types/recipe";

export default defineComponent({
  components: { RecipeCardSection },
  setup() {
    const api = useUserApi();
    const route = useRoute();
    const router = useRouter();
    const slug = route.value.params.slug;

    const state = reactive({
      initialValue: "",
      edit: false,
    });

    const tools = useAsync(async () => {
      const { data } = await api.tools.byslug(slug);
      if (data) {
        state.initialValue = data.name;
      }
      return data;
    }, slug);

    function reset() {
      state.edit = false;

      if (tools.value) {
        tools.value.name = state.initialValue;
      }
    }

    async function updateTools() {
      state.edit = false;

      if (!tools.value) {
        return;
      }
      const { data } = await api.tools.updateOne(tools.value.id, tools.value);

      if (data) {
        router.push("/recipes/tools/" + data.slug);
      }
    }

    return {
      tools,
      reset,
      ...toRefs(state),
      updateTools,
    };
  },
  head() {
    return {
      title: this.$t("tool.tools") as string,
    };
  },
  methods: {
    assignSorted(val: Array<Recipe>) {
      if (this.tools) {
        this.tools.recipes = val;
      }
    },
  },
});
</script>
