import type { VForm as VuetifyForm } from "vuetify/components/VForm";

type FormFieldType = "text" | "textarea" | "list" | "select" | "object" | "boolean" | "color" | "password";

export interface FormSelectOption {
  text: string;
  description?: string;
}

export interface FormField {
  section?: string;
  sectionDetails?: string;
  label?: string;
  hint?: string;
  varName: string;
  type: FormFieldType;
  rules?: string[];
  disableUpdate?: boolean;
  disableCreate?: boolean;
  options?: FormSelectOption[];
}

export type AutoFormItems = FormField[];

export type VForm = InstanceType<typeof VuetifyForm>;
