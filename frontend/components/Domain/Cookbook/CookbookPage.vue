<template>
  <div>
    <!-- Edit Dialog -->
    <BaseDialog
      v-if="editTarget"
      v-model="dialogStates.edit"
      width="100%"
      max-width="1100px"
      :icon="$globals.icons.pages"
      :title="$tc('general.edit')"
      :submit-icon="$globals.icons.save"
      :submit-text="$tc('general.save')"
      :submit-disabled="!editTarget.queryFilterString"
      @submit="editCookbook"
    >
      <v-card-text>
        <CookbookEditor :cookbook="editTarget" :actions="actions" />
      </v-card-text>
    </BaseDialog>

    <!-- Page -->
    <v-container v-if="book" fluid>
      <v-app-bar color="transparent" flat class="mt-n1">
        <v-icon large left> {{ $globals.icons.pages }} </v-icon>
        <v-toolbar-title class="headline"> {{ book.name }} </v-toolbar-title>
        <v-spacer></v-spacer>
        <BaseButton
          v-if="canEdit"
          class="mx-1"
          :edit="true"
          @click="handleEditCookbook"
        />
      </v-app-bar>
      <v-card flat>
        <v-card-text class="py-0">
          {{ book.description }}
        </v-card-text>
      </v-card>

      <v-container class="pa-0">
        <RecipeCardSection
          class="mb-5 mx-1"
          :recipes="recipes"
          :query="{ cookbook: slug }"
          @sortRecipes="assignSorted"
          @replaceRecipes="replaceRecipes"
          @appendRecipes="appendRecipes"
          @delete="removeRecipe"
        />
      </v-container>
    </v-container>
  </div>
</template>

  <script lang="ts">
  import { computed, defineComponent, useRoute, ref, useContext, useMeta, reactive, useRouter } from "@nuxtjs/composition-api";
  import { useLazyRecipes } from "~/composables/recipes";
  import RecipeCardSection from "@/components/Domain/Recipe/RecipeCardSection.vue";
  import { useCookbook, useCookbooks } from "~/composables/use-group-cookbooks";
  import { useLoggedInState } from "~/composables/use-logged-in-state";
  import { RecipeCookBook } from "~/lib/api/types/cookbook";
  import CookbookEditor from "~/components/Domain/Cookbook/CookbookEditor.vue";

  export default defineComponent({
    components: { RecipeCardSection, CookbookEditor },
    setup() {
      const { $auth } = useContext();
      const { isOwnGroup } = useLoggedInState();

      const route = useRoute();
      const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");

      const { recipes, appendRecipes, assignSorted, removeRecipe, replaceRecipes } = useLazyRecipes(isOwnGroup.value ? null : groupSlug.value);
      const slug = route.value.params.slug;
      const { getOne } = useCookbook(isOwnGroup.value ? null : groupSlug.value);
      const { actions } = useCookbooks();
      const router = useRouter();

      const tab = ref(null);
      const book = getOne(slug);

      const isOwnHousehold = computed(() => {
        if (!($auth.user && book.value?.householdId)) {
          return false;
        }

        return $auth.user.householdId === book.value.householdId;
      })
      const canEdit = computed(() => isOwnGroup.value && isOwnHousehold.value);

      const dialogStates = reactive({
        edit: false,
      });

      const editTarget = ref<RecipeCookBook | null>(null);
      function handleEditCookbook() {
        dialogStates.edit = true;
        editTarget.value = book.value;
      }

      async function editCookbook() {
        if (!editTarget.value) {
          return;
        }
        const response = await actions.updateOne(editTarget.value);

        // if name changed, redirect to new slug
        if (response?.slug && book.value?.slug !== response?.slug) {
          router.push(`/g/${route.value.params.groupSlug}/cookbooks/${response?.slug}`);
        }
        dialogStates.edit = false;
        editTarget.value = null;
      }

      useMeta(() => {
        return {
          title: book?.value?.name || "Cookbook",
        };
      });

      return {
        book,
        slug,
        tab,
        appendRecipes,
        assignSorted,
        recipes,
        removeRecipe,
        replaceRecipes,
        canEdit,
        dialogStates,
        editTarget,
        handleEditCookbook,
        editCookbook,
        actions,
      };
    },
    head: {}, // Must include for useMeta
  });
  </script>
