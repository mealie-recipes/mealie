import { fieldTypes } from "../forms";
import { AutoFormItems } from "~/types/auto-forms";

export const useUserForm = () => {
  const userForm: AutoFormItems = [
    {
      section: "User Details",
      label: "User Name",
      varName: "username",
      type: fieldTypes.TEXT,
      rules: ["required"],
    },
    {
      label: "Full Name",
      varName: "fullName",
      type: fieldTypes.TEXT,
      rules: ["required"],
    },
    {
      label: "Email",
      varName: "email",
      type: fieldTypes.TEXT,
      rules: ["required"],
    },
    {
      label: "Password",
      varName: "password",
      disableUpdate: true,
      type: fieldTypes.PASSWORD,
      rules: ["required"],
    },
    {
      section: "Permissions",
      label: "Administrator",
      varName: "admin",
      type: fieldTypes.BOOLEAN,
      rules: ["required"],
    },
    {
      label: "User can invite other to group",
      varName: "canInvite",
      type: fieldTypes.BOOLEAN,
      rules: ["required"],
    },
    {
      label: "User can manage group",
      varName: "canManage",
      type: fieldTypes.BOOLEAN,
      rules: ["required"],
    },
    {
      label: "User can organize group data",
      varName: "canOrganize",
      type: fieldTypes.BOOLEAN,
      rules: ["required"],
    },
    {
      label: "Enable advanced features",
      varName: "advanced",
      type: fieldTypes.BOOLEAN,
      rules: ["required"],
    },
  ];

  return {
    userForm,
  };
};
