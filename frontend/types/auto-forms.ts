type FormFieldType = "text" | "textarea" | "list" | "select" | "object" | "boolean" | "color" | "password";

export interface FormField {
  section?: string;
  sectionDetails?: string;
  label?: string;
  varName: string;
  type: FormFieldType;
  rules?: string[];
  disableUpdate?: boolean;
}

export type AutoFormItems = FormField[];
