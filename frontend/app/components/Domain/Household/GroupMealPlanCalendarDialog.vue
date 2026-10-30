<template>
  <BaseDialog
    v-model="dialog"
    :title="$t('meal-plan.calendar-feed')"
    :icon="$globals.icons.calendar"
    width="600"
    disable-submit-on-enter
  >
    <v-card-text>
      <p class="mb-4">
        {{ $t("meal-plan.calendar-feed-description") }}
      </p>

      <template v-if="loading">
        <v-progress-linear indeterminate />
      </template>
      <template v-else-if="!token">
        <p>
          {{ $t("meal-plan.calendar-feed-off") }}
          <span v-if="!canManage">{{ $t("meal-plan.calendar-feed-ask-manager") }}</span>
        </p>
      </template>
      <template v-else>
        <v-select
          v-model="selectedTypes"
          :items="planTypeOptions"
          item-title="text"
          item-value="value"
          :label="$t('meal-plan.meal-type')"
          multiple
          chips
          closable-chips
        />
        <v-checkbox
          v-model="includeNotes"
          :label="$t('meal-plan.calendar-feed-include-notes')"
          density="compact"
          hide-details
          class="mb-4"
        />

        <p class="text-caption mb-2">
          {{ $t("meal-plan.calendar-feed-times-hint") }}
        </p>
        <v-row dense>
          <v-col
            v-for="option in selectedOptions"
            :key="option.value"
            cols="6"
            sm="4"
          >
            <v-text-field
              v-model="times[option.value]"
              :label="option.text"
              type="time"
              density="compact"
              clearable
              hide-details
            />
          </v-col>
        </v-row>
        <v-number-input
          v-if="hasTimes"
          v-model="duration"
          :label="$t('meal-plan.calendar-feed-duration')"
          :min="1"
          :max="24 * 60"
          control-variant="hidden"
          class="mt-4"
        />

        <v-divider class="my-6" />
        <p class="text-subtitle-1 font-weight-bold">
          {{ $t("meal-plan.calendar-feed-event-details") }}
        </p>

        <div class="my-1">
          <p class="text-caption">
            {{ $t("meal-plan.calendar-feed-event-details-description") }}
          </p>
          <p class="pt-2">
            {{ $t("meal-plan.calendar-feed-event-details-change-warning") }}
          </p>
        </div>
        <DocLink
          class="mt-2 mb-4"
          link="/documentation/getting-started/features/#calendar-feed"
        />
        <v-text-field
          v-model="summary"
          :label="$t('meal-plan.calendar-feed-event-title')"
        />
        <v-textarea
          v-model="description"
          :label="$t('meal-plan.calendar-feed-event-description')"
          rows="2"
          auto-grow
          hide-details
        />

        <v-divider class="my-6" />
        <v-text-field
          :model-value="feedUrl"
          :label="$t('meal-plan.calendar-feed-url')"
          readonly
        >
          <template #append>
            <AppButtonCopy
              :copy-text="feedUrl"
              icon
            />
          </template>
        </v-text-field>
        <p
          v-if="canManage"
          class="text-caption"
        >
          {{ $t("meal-plan.calendar-feed-reset-hint") }}
        </p>
      </template>
    </v-card-text>

    <template
      v-if="canManage && !loading"
      #custom-card-action
    >
      <template v-if="token">
        <BaseButton
          delete
          :icon="$globals.icons.close"
          :text="$t('meal-plan.calendar-feed-turn-off')"
          @click="disableFeed"
        />
        <BaseButton
          edit
          :icon="$globals.icons.refresh"
          :text="$t('general.reset')"
          @click="createToken"
        />
      </template>
      <BaseButton
        v-else
        create
        :text="$t('meal-plan.calendar-feed-turn-on')"
        @click="createToken"
      />
    </template>
  </BaseDialog>
</template>

<script setup lang="ts">
import { whenever } from "@vueuse/core";
import { useUserApi } from "~/composables/api";
import { usePlanTypeOptions } from "~/composables/use-group-mealplan";
import type { PlanEntryType } from "~/lib/api/types/meal-plan";

const dialog = defineModel<boolean>({ default: false });

// must match the feed's defaults (mealplan_ical_service.py)
const EVENT_DURATION_MINUTES = 60;
const SUMMARY_TEMPLATE = "${type}: ${title}";
const DESCRIPTION_TEMPLATE = "${text}\n\n${url}";

const api = useUserApi();
const auth = useMealieAuth();
const canManage = computed(() => !!auth.user.value?.canManageHousehold);
const planTypeOptions = usePlanTypeOptions();

const loading = ref(false);
const token = ref<string | null>(null);

const selectedTypes = ref<PlanEntryType[]>(planTypeOptions.map(option => option.value));
const includeNotes = ref(true);
const times = ref<Partial<Record<PlanEntryType, string | null>>>({});
const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
const duration = ref<number | null>(EVENT_DURATION_MINUTES);
const summary = ref(SUMMARY_TEMPLATE);
const description = ref(DESCRIPTION_TEMPLATE);

const selectedOptions = computed(() => planTypeOptions.filter(option => selectedTypes.value.includes(option.value)));
const hasTimes = computed(() => selectedOptions.value.some(option => times.value[option.value]));

const feedUrl = computed(() => {
  if (!token.value) {
    return "";
  }

  const params = new URLSearchParams();
  if (selectedTypes.value.length && selectedTypes.value.length < planTypeOptions.length) {
    selectedTypes.value.forEach(type => params.append("types", type));
  }
  if (!includeNotes.value) {
    params.set("includeNotes", "false");
  }
  for (const option of selectedOptions.value) {
    const time = times.value[option.value];
    if (time) {
      params.set(option.value, time);
    }
  }
  if (hasTimes.value && timezone) {
    params.set("tz", timezone);
  }
  if (hasTimes.value && duration.value && duration.value !== EVENT_DURATION_MINUTES) {
    params.set("duration", duration.value.toString());
  }
  // blank templates fall back to the defaults
  if (summary.value?.trim() && summary.value !== SUMMARY_TEMPLATE) {
    params.set("summary", summary.value);
  }
  if (description.value?.trim() && description.value !== DESCRIPTION_TEMPLATE) {
    params.set("description", description.value);
  }

  const query = params.toString();
  return `${window.location.origin}/api/households/mealplans/ical/${token.value}${query ? `?${query}` : ""}`;
});

async function refreshToken() {
  loading.value = true;
  const { data } = await api.mealplans.getICalToken();
  token.value = data?.mealplanIcalToken ?? null;
  loading.value = false;
}

async function createToken() {
  const { data } = await api.mealplans.createICalToken();
  if (data) {
    token.value = data.mealplanIcalToken ?? null;
  }
}

async function disableFeed() {
  const { data } = await api.mealplans.deleteICalToken();
  if (data) {
    token.value = null;
  }
}

whenever(dialog, refreshToken);
</script>
