import type { VForm as VuetifyForm } from "vuetify/components/VForm";

type FormFieldType = "text" | "textarea" | "list" | "select" | "object" | "boolean" | "color" | "password";

export type FormValidationRule = (value: any) => boolean | string;

export interface FormSelectOption {
  text: string;
  value?: string;
}

export interface FormField {
  section?: string;
  sectionDetails?: string;
  cols?: number | "auto";
  label?: string;
  hint?: string;
  varName: string;
  type: FormFieldType;
  rules?: FormValidationRule[];
  disableUpdate?: boolean;
  disableCreate?: boolean;
  options?: FormSelectOption[];
  selectReturnValue?: "text" | "value";
}

export type AutoFormItems = FormField[];

export type VForm = InstanceType<typeof VuetifyForm>;
