import { fieldTypes } from "../forms";
import type { AutoFormItems } from "~/types/auto-forms";

export const useCommonSettingsForm = () => {
  const i18n = useI18n();

  const commonSettingsForm: AutoFormItems = [
    {
      section: i18n.t("profile.group-settings"),
      label: i18n.t("group.enable-public-access"),
      hint: i18n.t("group.enable-public-access-description"),
      varName: "makeGroupRecipesPublic",
      type: fieldTypes.BOOLEAN,
      rules: ["required"],
    },
    {
      section: i18n.t("data-pages.data-management"),
      label: i18n.t("user-registration.use-seed-data"),
      hint: i18n.t("user-registration.use-seed-data-description"),
      varName: "useSeedData",
      type: fieldTypes.BOOLEAN,
      rules: ["required"],
    },
  ];

  return {
    commonSettingsForm,
  };
};
