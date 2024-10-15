import { computed, useContext } from "@nuxtjs/composition-api";
import { Organizer, RecipeOrganizer } from "~/lib/api/types/non-generated";
import { LogicalOperator, RelationalKeyword, RelationalOperator } from "~/lib/api/types/response";

export interface FieldLogicalOperator {
  label: string;
  value: LogicalOperator;
}

export interface FieldRelationalOperator {
  label: string;
  value: RelationalKeyword | RelationalOperator;
}

export interface OrganizerBase {
  id: string;
  slug: string;
  name: string;
}

export type FieldType =
  | "string"
  | "number"
  | "boolean"
  | "date"
  | RecipeOrganizer;

export type FieldValue =
  | string
  | number
  | boolean
  | Date
  | Organizer;

export interface SelectableItem {
  label: string;
  value: FieldValue;
};

export interface FieldDefinition {
  name: string;
  label: string;
  type: FieldType;

  // only for select/organizer fields
  fieldOptions?: SelectableItem[];
}

export interface Field extends FieldDefinition {
  leftParenthesis?: string;
  logicalOperator?: FieldLogicalOperator;
  value: FieldValue;
  relationalOperatorValue: FieldRelationalOperator;
  relationalOperatorOptions: FieldRelationalOperator[];
  rightParenthesis?: string;

  // only for select/organizer fields
  values: FieldValue[];
  organizers: OrganizerBase[];
}

export function useQueryFilterBuilder() {
  const { i18n } = useContext();

  const logOps = computed<Record<LogicalOperator, FieldLogicalOperator>>(() => {
    const AND = {
      label: i18n.tc("query-filter.logical-operators.and"),
      value: "AND",
    } as FieldLogicalOperator;

    const OR = {
      label: i18n.tc("query-filter.logical-operators.or"),
      value: "OR",
    } as FieldLogicalOperator;

    return {
      AND,
      OR,
    };
  });

  const relOps = computed<Record<RelationalKeyword | RelationalOperator, FieldRelationalOperator>>(() => {
    const EQ = {
      label: i18n.tc("query-filter.relational-operators.equals"),
      value: "=",
    } as FieldRelationalOperator;

    const NOT_EQ = {
      label: i18n.tc("query-filter.relational-operators.does-not-equal"),
      value: "<>",
    } as FieldRelationalOperator;

    const GT = {
      label: i18n.tc("query-filter.relational-operators.is-greater-than"),
      value: ">",
    } as FieldRelationalOperator;

    const GTE = {
      label: i18n.tc("query-filter.relational-operators.is-greater-than-or-equal-to"),
      value: ">=",
    } as FieldRelationalOperator;

    const LT = {
      label: i18n.tc("query-filter.relational-operators.is-less-than"),
      value: "<",
    } as FieldRelationalOperator;

    const LTE = {
      label: i18n.tc("query-filter.relational-operators.is-less-than-or-equal-to"),
      value: "<=",
    } as FieldRelationalOperator;

    const IS = {
      label: i18n.tc("query-filter.relational-keywords.is"),
      value: "IS",
    } as FieldRelationalOperator;

    const IS_NOT = {
      label: i18n.tc("query-filter.relational-keywords.is-not"),
      value: "IS NOT",
    } as FieldRelationalOperator;

    const IN = {
      label: i18n.tc("query-filter.relational-keywords.is-one-of"),
      value: "IN",
    } as FieldRelationalOperator;

    const NOT_IN = {
      label: i18n.tc("query-filter.relational-keywords.is-not-one-of"),
      value: "NOT IN",
    } as FieldRelationalOperator;

    const CONTAINS_ALL = {
      label: i18n.tc("query-filter.relational-keywords.contains-all-of"),
      value: "CONTAINS ALL",
    } as FieldRelationalOperator;

    const LIKE = {
      label: i18n.tc("query-filter.relational-keywords.is-like"),
      value: "LIKE",
    } as FieldRelationalOperator;

    const NOT_LIKE = {
      label: i18n.tc("query-filter.relational-keywords.is-not-like"),
      value: "NOT LIKE",
    } as FieldRelationalOperator;

    /* eslint-disable object-shorthand */
    return {
      "=": EQ,
      "<>": NOT_EQ,
      ">": GT,
      ">=": GTE,
      "<": LT,
      "<=": LTE,
      "IS": IS,
      "IS NOT": IS_NOT,
      "IN": IN,
      "NOT IN": NOT_IN,
      "CONTAINS ALL": CONTAINS_ALL,
      "LIKE": LIKE,
      "NOT LIKE": NOT_LIKE,
    };
    /* eslint-enable object-shorthand */
  });

  function isOrganizerType(type: FieldType): type is Organizer {
    return (
      type === Organizer.Category ||
      type === Organizer.Tag ||
      type === Organizer.Tool ||
      type === Organizer.Food ||
      type === Organizer.Household
    );
  };

  function getFieldFromFieldDef(field: Field | FieldDefinition, resetValue = false): Field {
    /* eslint-disable dot-notation */
    const updatedField = {logicalOperator: logOps.value.AND, ...field} as Field;
    let operatorOptions: FieldRelationalOperator[];
    if (updatedField.fieldOptions?.length || isOrganizerType(updatedField.type)) {
      operatorOptions = [
        relOps.value["IN"],
        relOps.value["NOT IN"],
        relOps.value["CONTAINS ALL"],
      ];
    } else {
      switch (updatedField.type) {
        case "string":
          operatorOptions = [
            relOps.value["="],
            relOps.value["<>"],
            relOps.value["LIKE"],
            relOps.value["NOT LIKE"],
          ];
          break;
        case "number":
          operatorOptions = [
            relOps.value["="],
            relOps.value["<>"],
            relOps.value[">"],
            relOps.value[">="],
            relOps.value["<"],
            relOps.value["<="],
          ];
          break;
        case "boolean":
          operatorOptions = [relOps.value["="]];
          break;
        case "date":
          operatorOptions = [
          relOps.value["="],
            relOps.value["<>"],
            relOps.value[">"],
            relOps.value[">="],
            relOps.value["<"],
            relOps.value["<="],
          ];
          break;
        default:
          operatorOptions = [relOps.value["="], relOps.value["<>"]];
      }
    }
    updatedField.relationalOperatorOptions = operatorOptions;
    if (!operatorOptions.includes(updatedField.relationalOperatorValue)) {
      updatedField.relationalOperatorValue = operatorOptions[0];
    }

    if (resetValue) {
      updatedField.value = "";
      updatedField.values = [];
      updatedField.organizers = [];
    } else {
      updatedField.value = updatedField.value || "";
      updatedField.values = updatedField.values || [];
      updatedField.organizers = updatedField.organizers || [];
    }

    return updatedField;
    /* eslint-enable dot-notation */
  };

  function buildQueryFilterString(fields: Field[], useParenthesis: boolean): string {
    let isValid = true;
    let lParenCounter = 0;
    let rParenCounter = 0;

    const parts: string[] = [];
    fields.forEach((field, index) => {
      if (index) {
        if (!field.logicalOperator) {
          field.logicalOperator = logOps.value.AND;
        }
        parts.push(field.logicalOperator.value);
      }

      if (field.leftParenthesis && useParenthesis) {
        lParenCounter += field.leftParenthesis.length;
        parts.push(field.leftParenthesis);
      }

      if (field.label) {
        parts.push(field.name);
      } else {
        isValid = false;
      }

      if (field.relationalOperatorValue) {
        parts.push(field.relationalOperatorValue.value);
      } else if (field.type !== "boolean") {
        isValid = false;
      }

      if (field.fieldOptions?.length || isOrganizerType(field.type)) {
        if (field.values?.length) {
          let val: string;
          if (field.type === "string" || field.type === "date" || isOrganizerType(field.type)) {
            val = field.values.map((value) => `"${value.toString()}"`).join(",");
          } else {
            val = field.values.join(",");
          }
          parts.push(`[${val}]`);
        } else {
          isValid = false;
        }
      } else if (field.value) {
        if (field.type === "string" || field.type === "date") {
          parts.push(`"${field.value.toString()}"`);
        } else {
          parts.push(field.value.toString());
        }
      } else if (field.type === "boolean") {
        parts.push("false");
      } else {
        isValid = false;
      }

      if (field.rightParenthesis && useParenthesis) {
        rParenCounter += field.rightParenthesis.length;
        parts.push(field.rightParenthesis);
      }
    });

    if (lParenCounter !== rParenCounter) {
      isValid = false;
    }

    return isValid ? parts.join(" ") : "";
  }

  return {
    logOps,
    relOps,
    buildQueryFilterString,
    getFieldFromFieldDef,
    isOrganizerType,
  };
}
