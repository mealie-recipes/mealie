import { useContext } from "@nuxtjs/composition-api";
import { fieldTypes } from "../forms";
import { AutoFormItems } from "~/types/auto-forms";

export const useCommonSettingsForm = () => {
    const { i18n } = useContext();

    const commonSettingsForm: AutoFormItems = [
        {
          section: i18n.tc("profile.group-settings"),
          label: i18n.tc("group.enable-public-access"),
          hint: i18n.tc("group.enable-public-access-description"),
          varName: "makeGroupRecipesPublic",
          type: fieldTypes.BOOLEAN,
          rules: ["required"],
        },
        {
          section: i18n.tc("data-pages.data-management"),
          label: i18n.tc("user-registration.use-seed-data"),
          hint: i18n.tc("user-registration.use-seed-data-description"),
          varName: "useSeedData",
          type: fieldTypes.BOOLEAN,
          rules: ["required"],
        },
      ];

    return {
        commonSettingsForm,
    }
}
