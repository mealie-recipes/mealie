<template>
  <div>
    <v-card-title class="headline">
      {{ $t('recipe.create-recipe') }}
    </v-card-title>
    <v-card-text>
      {{ $t('recipe.create-a-recipe-by-providing-the-name-all-recipes-must-have-unique-names') }}
      <v-form
        ref="domCreateByName"
        @submit.prevent
      >
        <v-text-field
          v-model="newRecipeName"
          :label="$t('recipe.recipe-name')"
          :prepend-inner-icon="$globals.icons.primary"
          validate-on="blur"
          autofocus
          variant="solo-filled"
          clearable
          class="rounded-lg mt-2"
          color="primary"
          rounded
          :rules="[validators.required]"
          :hint="$t('recipe.new-recipe-names-must-be-unique')"
          persistent-hint
          @keyup.enter="createByName(newRecipeName)"
        />
      </v-form>

      <v-expand-transition>
        <v-alert
          v-if="duplicateMatches.length > 0"
          type="warning"
          variant="tonal"
          class="mt-4 rounded-lg"
          border="start"
        >
          <div class="d-flex align-center justify-space-between mb-1">
            <div class="text-subtitle-1 font-weight-bold d-flex align-center">
              <v-chip size="small" color="warning" class="mr-2 font-weight-bold">
                {{ $t('recipe.duplicate-detected') }}
              </v-chip>
              {{ $t('recipe.duplicate-warning-title') }}
            </div>
          </div>
          <div class="text-body-2 mb-2">
            {{ $t('recipe.duplicate-warning-body') }}
          </div>
          <v-list density="compact" class="bg-transparent pa-0">
            <v-list-item
              v-for="match in duplicateMatches"
              :key="match.id"
              class="px-0 py-1"
            >
              <template #title>
                <span class="font-weight-medium">{{ match.name }}</span>
                <span class="text-caption text-medium-emphasis ml-2">({{ match.matchReason }})</span>
              </template>
              <template #append>
                <v-btn
                  size="small"
                  variant="outlined"
                  color="warning"
                  :to="`/g/${groupSlug}/r/${match.slug}`"
                  target="_blank"
                >
                  {{ $t('recipe.duplicate-view-existing') }}
                  <v-icon end size="small">mdi-open-in-new</v-icon>
                </v-btn>
              </template>
            </v-list-item>
          </v-list>
        </v-alert>
      </v-expand-transition>
    </v-card-text>
    <v-card-actions class="justify-center">
      <div style="width: 250px">
        <BaseButton
          :disabled="newRecipeName.trim() === ''"
          rounded
          block
          :loading="state.loading"
          @click="createByName(newRecipeName)"
        >
          {{ duplicateMatches.length > 0 ? $t('recipe.duplicate-create-anyway') : $t('recipe.create-recipe') }}
        </BaseButton>
      </div>
    </v-card-actions>
  </div>
</template>

<script setup lang="ts">
import type { AxiosResponse } from "axios";
import { useUserApi } from "~/composables/api";
import { validators } from "~/composables/use-validators";
import type { RecipeDuplicateMatchOut } from "~/lib/api/types/recipe";
import type { VForm } from "~/types/auto-forms";

const state = reactive({
  error: false,
  loading: false,
});
const auth = useMealieAuth();
const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");

const api = useUserApi();
const router = useRouter();

function handleResponse(response: AxiosResponse<string> | null, edit = false) {
  if (response?.status !== 201) {
    state.error = true;
    state.loading = false;
    return;
  }
  router.push(`/g/${groupSlug.value}/r/${response.data}?edit=${edit.toString()}`);
}

const newRecipeName = ref("");
const domCreateByName = ref<VForm | null>(null);
const duplicateMatches = ref<RecipeDuplicateMatchOut[]>([]);

let checkTimer: ReturnType<typeof setTimeout> | null = null;

watch(newRecipeName, (val) => {
  if (checkTimer) {
    clearTimeout(checkTimer);
  }
  const clean = val ? val.trim() : "";
  if (clean.length < 2) {
    duplicateMatches.value = [];
    return;
  }
  checkTimer = setTimeout(async () => {
    try {
      const { data } = await api.recipes.checkDuplicate({ name: clean });
      if (data?.isDuplicate && data.matches?.length) {
        duplicateMatches.value = data.matches;
      } else {
        duplicateMatches.value = [];
      }
    } catch {
      duplicateMatches.value = [];
    }
  }, 400);
});

async function createByName(name: string) {
  if (!domCreateByName.value?.validate() || name === "") {
    return;
  }
  const { response } = await api.recipes.createOne({ name });
  handleResponse(response as any, true);
}
</script>
