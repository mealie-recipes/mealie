import type { Composer } from "vue-i18n";
import type { GroupPreferencesPluralHandling } from "~/lib/api/types/group";

export type HandlingOption = {
  label: string;
  value: GroupPreferencesPluralHandling;
  example: string;
};

export function useGroupPluralHandlingOptions(i18n: Composer) {
  const pluralHandlingOptions = computed<HandlingOption[]>(() => [
    {
      label: i18n.t("group.pluralize-only-if-there-is-no-unit"),
      value: "pluralize_food_without_unit",
      example: i18n.t("group.pluralize-only-if-there-is-no-unit-example"),
    },
    {
      label: i18n.t("group.always-pluralize-even-if-there-is-a-unit"),
      value: "always_pluralize",
      example: i18n.t("group.always-pluralize-even-if-there-is-a-unit-example"),
    },
    {
      label: i18n.t("group.never-pluralize"),
      value: "disable",
      example: i18n.t("group.never-pluralize-example"),
    },
  ]);
  function pluralHandlingOptionsItemProps(item: HandlingOption) {
    return {
      title: item.label,
      subtitle: item.example,
    };
  }

  return {
    pluralHandlingOptions,
    pluralHandlingOptionsItemProps,
  }
}
