import type { TimelineEventType } from "~/lib/api/types/recipe";

export interface TimelineEventTypeData {
  value: TimelineEventType;
  label: string;
  icon: string;
}

export const useTimelineEventTypes = () => {
  const i18n = useI18n();
  const { $globals } = useNuxtApp();
  const eventTypeOptions = computed<TimelineEventTypeData[]>(() => {
    return [
      {
        value: "comment",
        label: i18n.t("recipe.comment"),
        icon: $globals.icons.commentTextMultiple,
      },
      {
        value: "info",
        label: i18n.t("settings.theme.info"),
        icon: $globals.icons.informationVariant,
      },
      {
        value: "system",
        label: i18n.t("general.system"),
        icon: $globals.icons.cog,
      },
    ];
  });

  return {
    eventTypeOptions,
  };
};
