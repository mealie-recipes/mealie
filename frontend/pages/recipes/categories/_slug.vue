<template>
  <v-container>
    <RecipeCardSection
      v-if="category"
      :icon="$globals.icons.tags"
      :title="category.name"
      :recipes="category.recipes"
      @sort="assignSorted"
    >
      <template #title>
        <v-btn icon class="mr-1">
          <v-icon dark large @click="reset">
            {{ $globals.icons.tags }}
          </v-icon>
        </v-btn>

        <template v-if="edit">
          <v-text-field
            v-model="category.name"
            autofocus
            single-line
            dense
            hide-details
            class="headline"
            @keyup.enter="updateCategory"
          >
          </v-text-field>
          <v-btn icon @click="updateCategory">
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
                {{ category.name }}
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

    const category = useAsync(async () => {
      const { data } = await api.categories.bySlug(slug);
      if (data) {
        state.initialValue = data.name;
      }
      return data;
    }, slug);

    function reset() {
      state.edit = false;

      if (category.value) {
        category.value.name = state.initialValue;
      }
    }

    async function updateCategory() {
      state.edit = false;

      if (!category.value) {
        return;
      }
      const { data } = await api.categories.updateOne(category.value.id, category.value);

      if (data) {
        router.push("/recipes/categories/" + data.slug);
      }
    }

    return {
      category,
      reset,
      ...toRefs(state),
      updateCategory,
    };
  },
  head() {
    return {
      title: this.$t("category.categories") as string,
    };
  },
  methods: {
    assignSorted(val: Array<Recipe>) {
      if (this.category) {
        this.category.recipes = val;
      }
    },
  },
});
</script>
