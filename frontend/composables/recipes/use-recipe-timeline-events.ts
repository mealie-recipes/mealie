import { computed, useContext } from "@nuxtjs/composition-api";
import { TimelineEventType } from "~/lib/api/types/recipe";

export interface TimelineEventTypeData {
  value: TimelineEventType;
  label: string;
  icon: string;
}

export const useTimelineEventTypes = () => {
  const { $globals, i18n } = useContext();
  const eventTypeOptions = computed<TimelineEventTypeData[]>(() => {
    return [
      {
        value: "comment",
        label: i18n.tc("recipe.comment"),
        icon: $globals.icons.commentTextMultiple,
      },
      {
        value: "info",
        label: i18n.tc("settings.theme.info"),
        icon: $globals.icons.informationVariant,
      },
      {
        value: "system",
        label: i18n.tc("general.system"),
        icon: $globals.icons.cog,
      },
    ];
  });

  return {
    eventTypeOptions,
  }
}
