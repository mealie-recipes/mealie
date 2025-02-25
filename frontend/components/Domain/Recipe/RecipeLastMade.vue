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
      <div class="d-flex justify-center flex-wrap">
        <v-chip
          label
          :small="$vuetify.breakpoint.smAndDown"
          color="accent custom-transparent"
          class="ma-1 pa-3"
        >
          <v-icon left>
            {{ $globals.icons.calendar }}
          </v-icon>
            <div v-if="lastMadeReady">
              {{ $t('recipe.last-made-date', { date: lastMade ? new Date(lastMade).toLocaleDateString($i18n.locale) : $t("general.never") } ) }}
            </div>
            <div v-else>
              <AppLoader tiny />
            </div>
        </v-chip>
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
    onMounted(async () => {
      if (!$auth.user?.householdSlug) {
        lastMade.value = props.recipe.lastMade;
      } else {
        const { data } = await userApi.households.getCurrentUserHouseholdRecipe(props.recipe.slug || "");
        lastMade.value = data?.lastMade;
      }

      lastMadeReady.value = true;
    });


    whenever(
      () => madeThisDialog.value,
      () => {
        // Set timestamp to now
        newTimelineEventTimestamp.value = (
          new Date(Date.now() - (new Date()).getTimezoneOffset() * 60000)
        ).toISOString().substring(0, 10);
      }
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

    const state = reactive({datePickerMenu: false});
    async function createTimelineEvent() {
      if (!(newTimelineEventTimestamp.value && props.recipe?.id && props.recipe?.slug)) {
        return;
      }

      newTimelineEvent.value.recipeId = props.recipe.id
      // @ts-expect-error - TS doesn't like the $auth global user attribute
      newTimelineEvent.value.subject = i18n.t("recipe.user-made-this", { user: $auth.user.fullName })

      // the user only selects the date, so we set the time to end of day local time
      // we choose the end of day so it always comes after "new recipe" events
      newTimelineEvent.value.timestamp = new Date(newTimelineEventTimestamp.value + "T23:59:59").toISOString();

      const eventResponse = await userApi.recipes.createTimelineEvent(newTimelineEvent.value);
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
      domMadeThisForm,
      madeThisDialog,
      firstDayOfWeek,
      newTimelineEvent,
      newTimelineEventImage,
      newTimelineEventImagePreviewUrl,
      newTimelineEventTimestamp,
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
