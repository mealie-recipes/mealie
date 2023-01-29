<template>
  <div>
    <div>
      <BaseDialog
        v-model="madeThisDialog"
        :icon="$globals.icons.chefHat"
        :title="$tc('recipe.made-this')"
        :submit-text="$tc('general.save')"
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
              <v-date-picker
                v-model="newTimelineEvent.timestamp"
                no-title
                :local="$i18n.locale"
                @input="datePickerMenu = false"
              />
            </v-menu>
          </v-form>
        </v-card-text>
      </BaseDialog>
    </div>
    <div>
      <div class="d-flex justify-center flex-wrap">
        <BaseButton :small="$vuetify.breakpoint.smAndDown" @click="madeThisDialog = true">
          <template #icon> {{ $globals.icons.chefHat }} </template>
          {{ $t('recipe.made-this') }}
        </BaseButton>
      </div>
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
            {{ $t('recipe.last-made-date', { date: value ? new Date(value+"Z").toLocaleDateString($i18n.locale) : $t("general.never") } ) }}
        </v-chip>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, toRefs, useContext } from "@nuxtjs/composition-api";
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
    const { $auth, i18n } = useContext();
    const domMadeThisForm = ref<VForm>();
    const newTimelineEvent = ref<RecipeTimelineEventIn>({
      // @ts-expect-error - TS doesn't like the $auth global user attribute
      // eslint-disable-next-line
      subject: i18n.t("recipe.user-made-this", { user: $auth.user.fullName } as string),
      eventType: "comment",
      eventMessage: "",
      timestamp: undefined,
    });

    whenever(
      () => madeThisDialog.value,
      () => {
        // Set timestamp to now
        newTimelineEvent.value.timestamp = (
          new Date(Date.now() - (new Date()).getTimezoneOffset() * 60000)
        ).toISOString().substring(0, 10);
      }
    );

    const state = reactive({datePickerMenu: false});
    async function createTimelineEvent() {
      if (!newTimelineEvent.value.timestamp) {
        return;
      }

      const actions: Promise<any>[] = [];

      // the user only selects the date, so we set the time to end of day local time
      // we choose the end of day so it always comes after "new recipe" events
      newTimelineEvent.value.timestamp = new Date(newTimelineEvent.value.timestamp + "T23:59:59").toISOString();
      actions.push(userApi.recipes.createTimelineEvent(props.recipeSlug, newTimelineEvent.value));

      // we also update the recipe's last made value
      if (!props.value || newTimelineEvent.value.timestamp > props.value) {
        const payload = {lastMade: newTimelineEvent.value.timestamp};
        actions.push(userApi.recipes.patchOne(props.recipeSlug, payload));

        // update recipe in parent so the user can see it
        // we remove the trailing "Z" since this is how the API returns it
        context.emit(
          "input", newTimelineEvent.value.timestamp
            .substring(0, newTimelineEvent.value.timestamp.length - 1)
        );
      }

      await Promise.allSettled(actions);

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
