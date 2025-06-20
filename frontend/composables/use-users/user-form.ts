import { fieldTypes } from "../forms";
import type { AutoFormItems } from "~/types/auto-forms";

export const useUserForm = () => {
  const i18n = useI18n();

  const userForm: AutoFormItems = [
    {
      section: i18n.t("user.user-details"),
      label: i18n.t("user.user-name"),
      varName: "username",
      type: fieldTypes.TEXT,
      rules: ["required"],
    },
    {
      label: i18n.t("user.full-name"),
      varName: "fullName",
      type: fieldTypes.TEXT,
      rules: ["required"],
    },
    {
      label: i18n.t("user.email"),
      varName: "email",
      type: fieldTypes.TEXT,
      rules: ["required"],
    },
    {
      label: i18n.t("user.password"),
      varName: "password",
      disableUpdate: true,
      type: fieldTypes.PASSWORD,
      rules: ["required", "minLength:8"],
    },
    {
      label: i18n.t("user.authentication-method"),
      varName: "authMethod",
      type: fieldTypes.SELECT,
      hint: i18n.t("user.authentication-method-hint"),
      disableCreate: true,
      options: [{ text: "Mealie" }, { text: "LDAP" }, { text: "OIDC" }],
    },
    {
      section: i18n.t("user.permissions"),
      label: i18n.t("user.administrator"),
      varName: "admin",
      type: fieldTypes.BOOLEAN,
      rules: ["required"],
    },
    {
      label: i18n.t("user.user-can-invite-other-to-group"),
      varName: "canInvite",
      type: fieldTypes.BOOLEAN,
      rules: ["required"],
    },
    {
      label: i18n.t("user.user-can-manage-group"),
      varName: "canManage",
      type: fieldTypes.BOOLEAN,
      rules: ["required"],
    },
    {
      label: i18n.t("user.user-can-organize-group-data"),
      varName: "canOrganize",
      type: fieldTypes.BOOLEAN,
      rules: ["required"],
    },
    {
      label: i18n.t("user.user-can-manage-household"),
      varName: "canManageHousehold",
      type: fieldTypes.BOOLEAN,
      rules: ["required"],
    },
    {
      label: i18n.t("user.enable-advanced-features"),
      varName: "advanced",
      type: fieldTypes.BOOLEAN,
      rules: ["required"],
    },
  ];

  return {
    userForm,
  };
};
