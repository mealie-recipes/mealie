import type { VForm as VuetifyForm } from "vuetify/components/VForm";

type FormFieldType = "text" | "textarea" | "list" | "select" | "object" | "boolean" | "color" | "password";

export type FormValidationRule = (value: any) => boolean | string;

export interface FormSelectOption {
  text: string;
}

export interface FormField {
  section?: string;
  sectionDetails?: string;
  label?: string;
  hint?: string;
  varName: string;
  type: FormFieldType;
  rules?: FormValidationRule[];
  disableUpdate?: boolean;
  disableCreate?: boolean;
  options?: FormSelectOption[];
  selectReturnValue?: string;
}

export type AutoFormItems = FormField[];

export type VForm = InstanceType<typeof VuetifyForm>;
