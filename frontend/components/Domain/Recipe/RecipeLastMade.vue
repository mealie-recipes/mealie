<template>
  <div>
    <div>
      <BaseDialog
        v-model="madeThisDialog"
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
                    <template #activator="{ props }">
                      <v-text-field
                        v-model="newTimelineEventTimestampString"
                        :prepend-icon="$globals.icons.calendar"
                        v-bind="props"
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
          <v-tooltip bottom>
            <template #activator="{ props }">
              <v-btn
                rounded
                variant="outlined"
                size="x-large"
                v-bind="props"
                style="border-color: rgb(var(--v-theme-primary));"
                @click="madeThisDialog = true"
              >
                <v-icon start size="large" color="primary">
                  {{ $globals.icons.calendar }}
                </v-icon>
                <span class="text-body-1 opacity-80">
                  <b>{{ $t("general.last-made") }}</b>
                  <br>
                  {{ lastMade ? new Date(lastMade).toLocaleDateString($i18n.locale) : $t("general.never") }}
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

<script lang="ts">
import { whenever } from "@vueuse/core";
import { useUserApi } from "~/composables/api";
import { useHouseholdSelf } from "~/composables/use-households";
import type { Recipe, RecipeTimelineEventIn } from "~/lib/api/types/recipe";
import type { VForm } from "~/types/auto-forms";

export default defineNuxtComponent({
  props: {
    recipe: {
      type: Object as () => Recipe,
      required: true,
    },
  },
  emits: ["eventCreated"],
  setup(props, context) {
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
      return newTimelineEventTimestamp.value.toISOString().substring(0, 10);
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

    whenever(
      () => madeThisDialog.value,
      () => {
        // Set timestamp to now
        newTimelineEventTimestamp.value = new Date(Date.now() - new Date().getTimezoneOffset() * 60000);
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

    const state = reactive({ datePickerMenu: false });
    async function createTimelineEvent() {
      if (!(newTimelineEventTimestampString.value && props.recipe?.id && props.recipe?.slug)) {
        return;
      }

      newTimelineEvent.value.recipeId = props.recipe.id;
      // Note: $auth.user is now a ref
      newTimelineEvent.value.subject = i18n.t("recipe.user-made-this", { user: $auth.user.value?.fullName });

      // the user only selects the date, so we set the time to end of day local time
      // we choose the end of day so it always comes after "new recipe" events
      newTimelineEvent.value.timestamp = new Date(newTimelineEventTimestampString.value + "T23:59:59").toISOString();

      const eventResponse = await userApi.recipes.createTimelineEvent(newTimelineEvent.value);
      const newEvent = eventResponse.data;

      // we also update the recipe's last made value
      if (!lastMade.value || newTimelineEvent.value.timestamp > lastMade.value) {
        lastMade.value = newTimelineEvent.value.timestamp;
        await userApi.recipes.updateLastMade(props.recipe.slug, newTimelineEvent.value.timestamp);
      }

      // update the image, if provided
      if (newTimelineEventImage.value && newEvent) {
        const imageResponse = await userApi.recipes.updateTimelineEventImage(
          newEvent.id,
          newTimelineEventImage.value,
          newTimelineEventImageName.value,
        );
        if (imageResponse.data) {
          newEvent.image = imageResponse.data.image;
        }
      }

      // reset form
      newTimelineEvent.value.eventMessage = "";
      newTimelineEvent.value.timestamp = undefined;
      clearImage();
      madeThisDialog.value = false;
      domMadeThisForm.value?.reset();

      context.emit("eventCreated", newEvent);
    }

    return {
      ...toRefs(state),
      domMadeThisForm,
      madeThisDialog,
      firstDayOfWeek,
      newTimelineEvent,
      newTimelineEventImage,
      newTimelineEventImagePreviewUrl,
      newTimelineEventTimestamp,
      newTimelineEventTimestampString,
      lastMade,
      lastMadeReady,
      createTimelineEvent,
      clearImage,
      uploadImage,
      updateUploadedImage,
    };
  },
});
</script>
