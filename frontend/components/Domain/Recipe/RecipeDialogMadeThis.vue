<template>
  <div>
    <BaseDialog
      v-model="dialog"
      :icon="$globals.icons.chefHat"
      title="I Made This"
      :submit-text="$tc('general.save')"
      @submit="createTimelineEvent"
      >
      <v-card-text>
        <v-form ref="domMadeThisForm">
          <v-textarea
            v-model="newTimelineEvent.eventMessage"
            autofocus
            label="Comment"
            hint="How did it turn out?"
            persistent-hint
            rows="4"
          ></v-textarea>
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
                v-model="newTimelineEvent.timestamp"
                :prepend-icon="$globals.icons.calendar"
                v-bind="attrs"
                readonly
                v-on="on"
              ></v-text-field>
            </template>
            <v-date-picker v-model="newTimelineEvent.timestamp" no-title @input="datePickerMenu = false"></v-date-picker>
          </v-menu>
        </v-form>
      </v-card-text>
    </BaseDialog>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, useContext, } from "@nuxtjs/composition-api";
import { whenever } from "@vueuse/core";
import { VForm } from "~/types/vuetify";
import { useUserApi } from "~/composables/api";
import { RecipeTimelineEventIn } from "~/lib/api/types/recipe";

export default defineComponent({
  props: {
    value: {
      type: Boolean,
      default: false,
    },
    recipeSlug: {
      type: String,
      required: true,
    },
  },
  setup(props, context) {
    // V-Model Support
    const dialog = computed({
      get: () => {
        return props.value;
      },
      set: (val) => {
        context.emit("input", val);
      },
    });

    const userApi = useUserApi();
    const { $auth } = useContext();
    const domMadeThisForm = ref<VForm>();
    const newTimelineEvent = ref<RecipeTimelineEventIn>({
      // @ts-expect-error - TS doesn't like the $auth global user attribute
      // eslint-disable-next-line
      subject: `${$auth.user.fullName} made this`,
      eventType: "info",
      eventMessage: "",
      timestamp: "",
    });

    const state = reactive({datePickerMenu: false});

    whenever(
      () => props.value,
      () => {
        // Set timestamp to now
        newTimelineEvent.value.timestamp = new Date().toISOString().substring(0, 10);
      }
    );

    async function createTimelineEvent() {
      // the user only selects the date, so we set the time to noon
      newTimelineEvent.value.timestamp += "T12:00:00";
      const timelineEventUpdate = userApi.recipes.createTimelineEvent(props.recipeSlug, newTimelineEvent.value);

      // we also update the recipe's last made value
      // TODO

      await Promise.allSettled([timelineEventUpdate])

      // reset form
      newTimelineEvent.value.eventMessage = "";
      dialog.value = false;
      domMadeThisForm.value?.reset();
    }

    return {
      ...toRefs(state),
      dialog,
      domMadeThisForm,
      newTimelineEvent,
      createTimelineEvent,
    };
  },
});
</script>
