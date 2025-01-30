<template>
  <div>
    <div>
      <BaseDialog
        v-model="madeThisDialog"
        :icon="$globals.icons.chefHat"
        :title="$tc('recipe.made-this')"
        :submit-text="$tc('recipe.add-to-timeline')"
        @submit="createTimelineEvent"
        >
        <v-card-text>
          <v-form ref="domMadeThisForm">
            <v-textarea
              v-model="newTimelineEvent.eventMessage"
              autofocus
              :label="$tc('recipe.comment')"
              :hint="$tc('recipe.how-did-it-turn-out')"
              persistent-hint
              rows="4"
            ></v-textarea>
            <v-container>
              <v-row>
                <v-col cols="auto">
                  <v-menu
                    v-model="datePickerMenu"
                    :close-on-content-click="false"
                    transition="scale-transition"
                    offset-y
                    max-width="290px"
                    min-width="auto"
                  >
                    <template #activator="{ on, attrs }">
                      <v-text-field
                        v-model="newTimelineEventTimestamp"
                        :prepend-icon="$globals.icons.calendar"
                        v-bind="attrs"
                        readonly
                        v-on="on"
                      ></v-text-field>
                    </template>
                    <v-date-picker
                      v-model="newTimelineEventTimestamp"
                      no-title
                      :first-day-of-week="firstDayOfWeek"
                      :local="$i18n.locale"
                      @input="datePickerMenu = false"
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
                    :text="$i18n.tc('recipe.upload-image')"
                    :text-btn="false"
                    :post="false"
                    @uploaded="uploadImage"
                  />
                  <v-btn
                    v-if="!!newTimelineEventImage"
                    color="error"
                    @click="clearImage"
                  >
                    <v-icon left>{{ $globals.icons.close }}</v-icon>
                    {{ $i18n.tc('recipe.remove-image') }}
                  </v-btn>
                </v-col>
              </v-row>
              <v-row
                v-if="newTimelineEventImage && newTimelineEventImagePreviewUrl"
              >
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
      <div class="d-flex justify-center flex-wrap">
        <!-- Wrap the chip in a v-menu so we can pick a date or set never -->
        <v-menu
          v-model="lastMadeMenu"
          :close-on-content-click="false"
          transition="scale-transition"
          offset-y
          max-width="290px"
          min-width="auto"
        >
          <template #activator="{ on, attrs }">
        <v-chip
          label
          :small="$vuetify.breakpoint.smAndDown"
          color="accent custom-transparent"
          class="ma-1 pa-3 hover-editable"
              v-bind="attrs"
              style="position: relative;"
              v-on="on"
        >
          <v-icon left>
            {{ $globals.icons.calendar }}
          </v-icon>
            <div v-if="lastMadeReady" class="last-made-text">
                {{ $t('recipe.last-made-date', {
                  date: lastMade
                    ? new Date(lastMade).toLocaleDateString($i18n.locale)
                    : $t("general.never")
                }) }}
            </div>
            <div v-else>
              <AppLoader tiny />
            </div>
            <div class="edit-last-made-text">
              {{ $t("general.edit") }}
            </div>
            <v-icon class="pencil-icon" small>
            mdi-pencil
          </v-icon>
        </v-chip>
          </template>

          <!-- Date picker to change lastMade -->
          <v-date-picker
            v-model="lastMadeEdit"
            no-title
            :first-day-of-week="firstDayOfWeek"
            :locale="$i18n.locale"
            @input="updateLastMade"
          />
          <v-card-actions>
            <v-spacer />
            <v-btn text @click="setNeverMade">
              {{ $t("general.never") }}
            </v-btn>
          </v-card-actions>
        </v-menu>
      </div>
      <div class="d-flex justify-center flex-wrap mt-1">
        <BaseButton :small="$vuetify.breakpoint.smAndDown" @click="madeThisDialog = true">
          <template #icon> {{ $globals.icons.chefHat }} </template>
          {{ $t('recipe.made-this') }}
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, ref, toRefs, useContext } from "@nuxtjs/composition-api";
import { whenever } from "@vueuse/core";
import { VForm } from "~/types/vuetify";
import { useUserApi } from "~/composables/api";
import { useHouseholdSelf } from "~/composables/use-households";
import { Recipe, RecipeTimelineEventIn } from "~/lib/api/types/recipe";

export default defineComponent({
  props: {
    recipe: {
      type: Object as () => Recipe,
      required: true,
    },
  },
  setup(props, context) {
    const madeThisDialog = ref(false);
    const userApi = useUserApi();
    const { household } = useHouseholdSelf();
    const { $auth, i18n } = useContext();
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
    const newTimelineEventTimestamp = ref<string>();

    const lastMade = ref(props.recipe.lastMade);
    const lastMadeReady = ref(false);
    // NEW: Toggle for menu, plus the date picker's local state
    const lastMadeMenu = ref(false);
    const lastMadeEdit = ref("");

    onMounted(async () => {
      if (!$auth.user?.householdSlug) {
        lastMade.value = props.recipe.lastMade;
      } else {
        const { data } = await userApi.households.getCurrentUserHouseholdRecipe(props.recipe.slug || "");
        lastMade.value = data?.lastMade;
      }

      lastMadeReady.value = true;

      // If lastMade exists, init the date picker to that date, else set to 'today'
      lastMadeEdit.value = lastMade.value
        ? new Date(lastMade.value).toISOString().substring(0, 10)
        : new Date().toISOString().substring(0, 10);
    });


    whenever(
      () => madeThisDialog.value,
      () => {
        // Set timestamp to now
        newTimelineEventTimestamp.value = new Date(
          Date.now() - new Date().getTimezoneOffset() * 60000
        )
          .toISOString()
          .substring(0, 10);
      }
    );

    const firstDayOfWeek = computed(() => {
      return household.value?.preferences?.firstDayOfWeek || 0;
    });

    // NEW: Update lastMade if user picks a date from the chip's date picker
    async function updateLastMade() {
      lastMadeMenu.value = false;
      if (!lastMadeEdit.value) {
        return setNeverMade();
      }
      const newDate = new Date(lastMadeEdit.value).toISOString();
      lastMade.value = newDate;
      await userApi.recipes.updateLastMade(props.recipe.slug, newDate);
    }

    // NEW: Clear lastMade (never made)
    async function setNeverMade() {
      lastMadeMenu.value = false;
      lastMade.value = null;
      lastMadeEdit.value = "";
      await userApi.recipes.updateLastMade(props.recipe.slug, null);
    }

    // Image logic
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

    const state = reactive({datePickerMenu: false});
    async function createTimelineEvent() {
      if (
        !(
          newTimelineEventTimestamp.value &&
          props.recipe?.id &&
          props.recipe?.slug
        )
      ) {
        return;
      }

      newTimelineEvent.value.recipeId = props.recipe.id
      // @ts-expect-error - TS doesn't like the $auth global user attribute
      newTimelineEvent.value.subject = i18n.t("recipe.user-made-this", { user: $auth.user.fullName })

      // the user only selects the date, so we set the time to end of day local time
      // we choose the end of day so it always comes after "new recipe" events
      newTimelineEvent.value.timestamp = new Date(newTimelineEventTimestamp.value + "T23:59:59").toISOString();

      const eventResponse = await userApi.recipes.createTimelineEvent(
        newTimelineEvent.value
      );
      const newEvent = eventResponse.data;

      // we also update the recipe's last made value
      if (!lastMade.value || newTimelineEvent.value.timestamp > lastMade.value) {
        lastMade.value = newTimelineEvent.value.timestamp;
        await userApi.recipes.updateLastMade(props.recipe.slug,  newTimelineEvent.value.timestamp);
      }

      // update the image, if provided
      if (newTimelineEventImage.value && newEvent) {
        const imageResponse = await userApi.recipes.updateTimelineEventImage(
          newEvent.id,
          newTimelineEventImage.value,
          newTimelineEventImageName.value,
        );
        if (imageResponse.data) {
          // @ts-ignore the image response data will always match a value of TimelineEventImage
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

      // Refs for the "I made this" dialog
      domMadeThisForm,
      madeThisDialog,
      newTimelineEvent,
      newTimelineEventTimestamp,
      newTimelineEventImage,
      newTimelineEventImageName,
      newTimelineEventImagePreviewUrl,
      // Computed
      firstDayOfWeek,

      // Original timeline creation
      createTimelineEvent,
      clearImage,
      uploadImage,
      updateUploadedImage,

      // Last made logic
      lastMade,
      lastMadeReady,
      lastMadeMenu,
      lastMadeEdit,
      updateLastMade,
      setNeverMade,
    };
  },
});
</script>
<style scoped>
.hover-editable {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: auto;
}

/* Default state: Show last-made text, hide edit message */
.last-made-text {
  opacity: 1;
  transition: opacity 0.2s ease;
}

/* Edit message: Centered inside the chip */
.edit-last-made-text {
  position: absolute;
  width: 100%;
  text-align: center; /* Center horizontally */
  top: 50%;
  transform: translateY(-50%);
  opacity: 0;
  transition: opacity 0.2s ease;
}

/* Hide last-made text & show edit message on hover */
.hover-editable:hover .last-made-text {
  opacity: 0;
}

.hover-editable:hover .edit-last-made-text {
  opacity: 1;
}

/* Position the pencil icon */
.pencil-icon {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0;
  transition: opacity 0.2s ease;
}

/* Show pencil on hover */
.hover-editable:hover .pencil-icon {
  opacity: 1;
}
</style>
