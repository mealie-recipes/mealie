<template>
  <div>
    <div>
      <BaseDialog
        v-model="madeThisDialog"
        :loading="madeThisFormLoading"
        :icon="$globals.icons.chefHat"
        :title="$t('recipe.made-this')"
        :submit-text="$t('recipe.add-to-timeline')"
        can-submit
        @submit="createTimelineEvent"
      >
        <v-card-text>
          <v-form ref="domMadeThisForm">
            <v-textarea
              v-model="newTimelineEvent.eventMessage"
              autofocus
              :label="$t('recipe.comment')"
              :hint="$t('recipe.how-did-it-turn-out')"
              persistent-hint
              rows="4"
            />
            <div v-if="childRecipes?.length">
              <v-card-text class="pt-6 pb-0">
                {{ $t('recipe.include-linked-recipes') }}
              </v-card-text>
              <v-list>
                <v-list-item
                  v-for="(childRecipe, i) in childRecipes"
                  :key="childRecipe.recipeId + i"
                  density="compact"
                  class="my-0 py-0"
                  @click="childRecipe.checked = !childRecipe.checked"
                >
                  <v-checkbox
                    hide-details
                    density="compact"
                    :input-value="childRecipe.checked"
                    :label="childRecipe.name"
                    class="my-0 py-0"
                    color="secondary"
                  />
                </v-list-item>
              </v-list>
            </div>
            <v-container>
              <v-row>
                <v-col cols="6">
                  <v-menu
                    v-model="datePickerMenu"
                    :close-on-content-click="false"
                    transition="scale-transition"
                    offset-y
                    max-width="290px"
                  >
                    <template #activator="{ props: activatorProps }">
                      <v-text-field
                        :model-value="$d(newTimelineEventTimestamp)"
                        :prepend-icon="$globals.icons.calendar"
                        v-bind="activatorProps"
                        readonly
                      />
                    </template>
                    <v-date-picker
                      v-model="newTimelineEventTimestamp"
                      hide-header
                      :first-day-of-week="firstDayOfWeek"
                      :local="$i18n.locale"
                      @update:model-value="datePickerMenu = false"
                    />
                  </v-menu>
                </v-col>
                <v-spacer />
                <v-col cols="auto" align-self="center">
                  <AppButtonUpload
                    v-if="!newTimelineEventImage"
                    class="ml-auto"
                    url="none"
                    file-name="image"
                    accept="image/*"
                    :text="$t('recipe.upload-image')"
                    :text-btn="false"
                    :post="false"
                    @uploaded="uploadImage"
                  />
                  <v-btn v-if="!!newTimelineEventImage" color="error" @click="clearImage">
                    <v-icon start>
                      {{ $globals.icons.close }}
                    </v-icon>
                    {{ $t("recipe.remove-image") }}
                  </v-btn>
                </v-col>
              </v-row>
              <v-row v-if="newTimelineEventImage && newTimelineEventImagePreviewUrl">
                <v-col cols="12" align-self="center">
                  <ImageCropper
                    :img="newTimelineEventImagePreviewUrl"
                    cropper-height="20vh"
                    cropper-width="100%"
                    @save="updateUploadedImage"
                  />
                </v-col>
              </v-row>
            </v-container>
          </v-form>
        </v-card-text>
      </BaseDialog>
    </div>
    <div>
      <div v-if="lastMadeReady" class="d-flex justify-center flex-wrap">
        <v-row no-gutters class="d-flex flex-wrap align-center" style="font-size: larger">
          <v-tooltip location="bottom">
            <template #activator="{ props: tooltipProps }">
              <v-btn
                rounded
                variant="outlined"
                size="x-large"
                v-bind="tooltipProps"
                style="border-color: rgb(var(--v-theme-primary));"
                @click="madeThisDialog = true"
              >
                <v-icon start size="large" color="primary">
                  {{ $globals.icons.calendar }}
                </v-icon>
                <span class="text-body-1 opacity-80">
                  <b>{{ $t("general.last-made") }}</b>
                  <br>
                  {{ lastMade ? $d(new Date(lastMade)) : $t("general.never") }}
                </span>
                <v-icon end size="large" color="primary">
                  {{ $globals.icons.createAlt }}
                </v-icon>
              </v-btn>
            </template>
            <span>{{ $t("recipe.made-this") }}</span>
          </v-tooltip>
        </v-row>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { whenever } from "@vueuse/core";
import { formatISO } from "date-fns";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { useHouseholdSelf } from "~/composables/use-households";
import type { Recipe, RecipeTimelineEventIn, RecipeTimelineEventOut } from "~/lib/api/types/recipe";
import type { VForm } from "~/types/auto-forms";

const props = defineProps<{ recipe: Recipe }>();
const emit = defineEmits<{
  eventCreated: [event: RecipeTimelineEventOut];
}>();

const madeThisDialog = ref(false);
const userApi = useUserApi();
const { household } = useHouseholdSelf();
const i18n = useI18n();
const $auth = useMealieAuth();
const domMadeThisForm = ref<VForm>();
const newTimelineEvent = ref<RecipeTimelineEventIn>({
  subject: "",
  eventType: "comment",
  eventMessage: "",
  timestamp: undefined,
  recipeId: props.recipe?.id || "",
});
const newTimelineEventImage = ref<Blob | File>();
const newTimelineEventImageName = ref<string>("");
const newTimelineEventImagePreviewUrl = ref<string>();
const newTimelineEventTimestamp = ref<Date>(new Date());
const newTimelineEventTimestampString = computed(() => {
  return formatISO(newTimelineEventTimestamp.value, { representation: "date" });
});

const lastMade = ref(props.recipe.lastMade);
const lastMadeReady = ref(false);
onMounted(async () => {
  if (!$auth.user?.value?.householdSlug) {
    lastMade.value = props.recipe.lastMade;
  }
  else {
    const { data } = await userApi.households.getCurrentUserHouseholdRecipe(props.recipe.slug || "");
    lastMade.value = data?.lastMade;
  }

  lastMadeReady.value = true;
});

const childRecipes = computed(() => {
  return props.recipe.recipeIngredient?.map((ingredient) => {
    if (ingredient.referencedRecipe) {
      return {
        checked: false, // Default value for checked
        recipeId: ingredient.referencedRecipe.id || "", // Non-nullable recipeId
        ...ingredient.referencedRecipe, // Spread the rest of the referencedRecipe properties
      };
    }
    else {
      return undefined;
    }
  }).filter(recipe => recipe !== undefined); // Filter out undefined values
});

whenever(
  () => madeThisDialog.value,
  () => {
    // Set timestamp to now
    newTimelineEventTimestamp.value = new Date();
  },
);

const firstDayOfWeek = computed(() => {
  return household.value?.preferences?.firstDayOfWeek || 0;
});

function clearImage() {
  newTimelineEventImage.value = undefined;
  newTimelineEventImageName.value = "";
  newTimelineEventImagePreviewUrl.value = undefined;
}

function uploadImage(fileObject: File) {
  newTimelineEventImage.value = fileObject;
  newTimelineEventImageName.value = fileObject.name;
  newTimelineEventImagePreviewUrl.value = URL.createObjectURL(fileObject);
}

function updateUploadedImage(fileObject: Blob) {
  newTimelineEventImage.value = fileObject;
  newTimelineEventImagePreviewUrl.value = URL.createObjectURL(fileObject);
}

const datePickerMenu = ref(false);
const madeThisFormLoading = ref(false);

function resetMadeThisForm() {
  madeThisFormLoading.value = false;

  newTimelineEvent.value.eventMessage = "";
  newTimelineEvent.value.timestamp = undefined;
  clearImage();
  madeThisDialog.value = false;
  domMadeThisForm.value?.reset();
}

async function createTimelineEvent() {
  if (!(newTimelineEventTimestampString.value && props.recipe?.id && props.recipe?.slug)) {
    return;
  }

  madeThisFormLoading.value = true;

  newTimelineEvent.value.recipeId = props.recipe.id;
  // Note: $auth.user is now a ref
  newTimelineEvent.value.subject = i18n.t("recipe.user-made-this", { user: $auth.user.value?.fullName });

  // the user only selects the date, so we set the time to end of day local time
  // we choose the end of day so it always comes after "new recipe" events
  newTimelineEvent.value.timestamp = new Date(newTimelineEventTimestampString.value + "T23:59:59").toISOString();

  let newEvent: RecipeTimelineEventOut | null = null;
  try {
    const eventResponse = await userApi.recipes.createTimelineEvent(newTimelineEvent.value);
    newEvent = eventResponse.data;
    if (!newEvent) {
      throw new Error("No event created");
    }
  }
  catch (error) {
    console.error("Failed to create timeline event:", error);
    alert.error(i18n.t("recipe.failed-to-add-to-timeline"));
    resetMadeThisForm();
    return;
  }

  // we also update the recipe's last made value
  if (!lastMade.value || newTimelineEvent.value.timestamp > lastMade.value) {
    try {
      lastMade.value = newTimelineEvent.value.timestamp;
      await userApi.recipes.updateLastMade(props.recipe.slug, newTimelineEvent.value.timestamp);
    }
    catch (error) {
      console.error("Failed to update last made date:", error);
      alert.error(i18n.t("recipe.failed-to-update-recipe"));
    }
  }

  for (const childRecipe of childRecipes.value || []) {
    if (!childRecipe.checked) {
      continue;
    }

    const childTimelineEvent = {
      ...newTimelineEvent.value,
      recipeId: childRecipe.recipeId,
      eventMessage: i18n.t("recipe.made-for-recipe", { recipe: childRecipe.name }),
      image: undefined,
    };
    try {
      await userApi.recipes.createTimelineEvent(childTimelineEvent);
    }
    catch (error) {
      console.error(`Failed to create timeline event for child recipe ${childRecipe.slug}:`, error);
    }

    if (
      newTimelineEvent.value.timestamp
      && (!childRecipe.lastMade || newTimelineEvent.value.timestamp > childRecipe.lastMade)
    ) {
      try {
        await userApi.recipes.updateLastMade(childRecipe.slug || "", newTimelineEvent.value.timestamp);
      }
      catch (error) {
        console.error(`Failed to update last made date for child recipe ${childRecipe.slug}:`, error);
      }
    }
  }

  // update the image, if provided
  let imageError = false;
  if (newTimelineEventImage.value) {
    try {
      const imageResponse = await userApi.recipes.updateTimelineEventImage(
        newEvent.id,
        newTimelineEventImage.value,
        newTimelineEventImageName.value,
      );
      if (imageResponse.data) {
        newEvent.image = imageResponse.data.image;
      }
    }
    catch (error) {
      imageError = true;
      console.error("Failed to upload image for timeline event:", error);
    }
  }
  if (imageError) {
    alert.error(i18n.t("recipe.added-to-timeline-but-failed-to-add-image"));
  }
  else {
    alert.success(i18n.t("recipe.added-to-timeline"));
  }

  resetMadeThisForm();
  emit("eventCreated", newEvent);
}
</script>
