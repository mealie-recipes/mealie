<template>
    <div>
      <div>
        <BaseDialog
          v-model="madeThisDialog"
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
      <div>
        <v-chip
          label
          color="accent custom-transparent"
          class="ma-1"
          style="height:100%;"
        >
          <v-icon left>
            {{ $globals.icons.calendar }}
          </v-icon>
            Last Made {{ value ? new Date(value).toLocaleDateString($i18n.locale) : "Never" }}
        </v-chip>
        <BaseButton @click="madeThisDialog = true">
          <template #icon> {{ $globals.icons.chefHat }} </template>
          I Made This
        </BaseButton>
      </div>
    </div>
  </template>

  <script lang="ts">
  import { defineComponent, reactive, ref, toRefs, useContext, } from "@nuxtjs/composition-api";
  import { whenever } from "@vueuse/core";
  import { VForm } from "~/types/vuetify";
  import { useUserApi } from "~/composables/api";
  import { RecipeTimelineEventIn } from "~/lib/api/types/recipe";

  export default defineComponent({
    props: {
      value: {
        type: String,
        default: null,
      },
      recipeSlug: {
        type: String,
        required: true,
      },
    },
    setup(props, context) {
      const madeThisDialog = ref(false);
      const userApi = useUserApi();
      const { $auth } = useContext();
      const domMadeThisForm = ref<VForm>();
      const newTimelineEvent = ref<RecipeTimelineEventIn>({
        // @ts-expect-error - TS doesn't like the $auth global user attribute
        // eslint-disable-next-line
        subject: `${$auth.user.fullName} made this`,
        eventType: "comment",
        eventMessage: "",
        timestamp: "",
      });

      const state = reactive({datePickerMenu: false});

      whenever(
        () => madeThisDialog.value,
        () => {
          // Set timestamp to now
          newTimelineEvent.value.timestamp = new Date().toISOString().substring(0, 10);
        }
      );

      async function createTimelineEvent() {
        if (!newTimelineEvent.value.timestamp) {
          return;
        }

        const actions: Promise<any>[] = []

        // the user only selects the date, so we set the time to noon
        newTimelineEvent.value.timestamp += "T12:00:00";
        actions.push(userApi.recipes.createTimelineEvent(props.recipeSlug, newTimelineEvent.value));

        // we also update the recipe's last made value
        if (!props.value || newTimelineEvent.value.timestamp > props.value) {
          const payload = {lastMade: newTimelineEvent.value.timestamp};
          actions.push(userApi.recipes.patchOne(props.recipeSlug, payload));

          // update recipe in parent so the user can see it
          context.emit("input", newTimelineEvent.value.timestamp);
        }

        await Promise.allSettled(actions)

        // reset form
        newTimelineEvent.value.eventMessage = "";
        madeThisDialog.value = false;
        domMadeThisForm.value?.reset();
      }

      return {
        ...toRefs(state),
        domMadeThisForm,
        madeThisDialog,
        newTimelineEvent,
        createTimelineEvent,
      };
    },
  });
  </script>
