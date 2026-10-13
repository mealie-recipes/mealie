<template>
  <div>
    <!-- Edit Dialog -->
    <BaseDialog
      v-if="editTarget"
      v-model="dialogStates.edit"
      width="100%"
      max-width="1100px"
      :icon="$globals.icons.pages"
      :title="$t('general.edit')"
      :submit-icon="$globals.icons.save"
      :submit-text="$t('general.save')"
      :submit-disabled="!editTarget.queryFilterString"
      can-submit
      @submit="editCookbook"
    >
      <v-card-text>
        <CookbookEditor
          v-model="editTarget"
        />
      </v-card-text>
    </BaseDialog>

    <div
      v-if="book"
      class="mealie-page"
    >
      <header class="mealie-page__header">
        <div class="mealie-page__titles">
          <div class="mealie-eyebrow">
            {{ $t("sidebar.cookbook") }}
          </div>
          <h1 class="mealie-page__title">
            {{ book.name }}
          </h1>
          <p v-if="book.description" class="cookbook-description">
            {{ book.description }}
          </p>
        </div>
        <div v-if="canEdit" class="mealie-page__actions">
          <button type="button" class="mealie-pill" @click="handleEditCookbook">
            <v-icon size="16">
              {{ $globals.icons.edit }}
            </v-icon>
            {{ $t("general.edit") }}
          </button>
        </div>
      </header>

      <div class="mealie-page__body">
        <RecipeCardSection
          :recipes="recipes"
          :query="{ cookbook: slug }"
          @sort-recipes="assignSorted"
          @replace-recipes="replaceRecipes"
          @append-recipes="appendRecipes"
          @delete="removeRecipe"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useLazyRecipes } from "~/composables/recipes";
import RecipeCardSection from "@/components/Domain/Recipe/RecipeCardSection.vue";
import { useCookbookStore } from "~/composables/store/use-cookbook-store";
import { useCookbook } from "~/composables/use-group-cookbooks";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import type { ReadCookBook } from "~/lib/api/types/cookbook";
import CookbookEditor from "~/components/Domain/Cookbook/CookbookEditor.vue";

const auth = useMealieAuth();
const { isOwnGroup } = useLoggedInState();

const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");

const { recipes, appendRecipes, assignSorted, removeRecipe, replaceRecipes } = useLazyRecipes(isOwnGroup.value ? null : groupSlug.value);
const slug = route.params.slug as string;
const { getOne } = useCookbook(isOwnGroup.value ? null : groupSlug.value);
const { actions } = useCookbookStore();
const router = useRouter();

const book = getOne(slug);

const isOwnHousehold = computed(() => {
  if (!(auth.user.value && book.value?.householdId)) {
    return false;
  }

  return auth.user.value.householdId === book.value.householdId;
});
const canEdit = computed(() => isOwnGroup.value && isOwnHousehold.value);

const dialogStates = reactive({
  edit: false,
});

const editTarget = ref<ReadCookBook | null>(null);
function handleEditCookbook() {
  dialogStates.edit = true;
  editTarget.value = book.value;
}

async function editCookbook() {
  if (!editTarget.value) {
    return;
  }
  const response = await actions.updateOne(editTarget.value);

  if (response?.slug && book.value?.slug !== response?.slug) {
    // if name changed, redirect to new slug
    router.push(`/g/${route.params.groupSlug}/cookbooks/${response?.slug}`);
  }
  else {
    // otherwise reload the page, since the recipe criteria changed
    router.go(0);
  }
  dialogStates.edit = false;
  editTarget.value = null;
}

useSeoMeta({
  title: book?.value?.name || "Cookbook",
});
</script>

<style scoped>
.cookbook-description {
  max-width: 640px;
  margin-top: 8px;
  font-size: 17px;
  line-height: 1.45;
  color: var(--mealie-text-secondary);
}
</style>
