import { Organizer } from "~/lib/api/types/non-generated";
import type { LogicalOperator, PlaceholderKeyword, RecipeOrganizer, RelationalKeyword, RelationalOperator } from "~/lib/api/types/non-generated";

export interface FieldLogicalOperator {
  label: string;
  value: LogicalOperator;
}

export interface FieldRelationalOperator {
  label: string;
  value: RelationalKeyword | RelationalOperator;
}

export interface FieldPlaceholderKeyword {
  label: string;
  value: PlaceholderKeyword;
}

export interface OrganizerBase {
  id: string;
  slug: string;
  name: string;
}

export type FieldType
  = | "string"
    | "number"
    | "boolean"
    | "date"
    | "relativeDate"
    | RecipeOrganizer;

export type FieldValue
  = | string
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

  // Select/Organizer
  fieldChoices?: SelectableItem[];
}

export interface Field extends FieldDefinition {
  leftParenthesis?: string;
  logicalOperator?: FieldLogicalOperator;
  value: FieldValue;
  relationalOperatorValue: FieldRelationalOperator;
  relationalOperatorChoices: FieldRelationalOperator[];
  rightParenthesis?: string;

  // Select/Organizer
  values: FieldValue[];
  organizers: OrganizerBase[];
}

export function useQueryFilterBuilder() {
  const i18n = useI18n();

  const logOps = computed<Record<LogicalOperator, FieldLogicalOperator>>(() => {
    const AND = {
      label: i18n.t("query-filter.logical-operators.and"),
      value: "AND",
    } as FieldLogicalOperator;

    const OR = {
      label: i18n.t("query-filter.logical-operators.or"),
      value: "OR",
    } as FieldLogicalOperator;

    return {
      AND,
      OR,
    };
  });

  const relOps = computed<Record<RelationalKeyword | RelationalOperator, FieldRelationalOperator>>(() => {
    const EQ = {
      label: i18n.t("query-filter.relational-operators.equals"),
      value: "=",
    } as FieldRelationalOperator;

    const NOT_EQ = {
      label: i18n.t("query-filter.relational-operators.does-not-equal"),
      value: "<>",
    } as FieldRelationalOperator;

    const GT = {
      label: i18n.t("query-filter.relational-operators.is-greater-than"),
      value: ">",
    } as FieldRelationalOperator;

    const GTE = {
      label: i18n.t("query-filter.relational-operators.is-greater-than-or-equal-to"),
      value: ">=",
    } as FieldRelationalOperator;

    const LT = {
      label: i18n.t("query-filter.relational-operators.is-less-than"),
      value: "<",
    } as FieldRelationalOperator;

    const LTE = {
      label: i18n.t("query-filter.relational-operators.is-less-than-or-equal-to"),
      value: "<=",
    } as FieldRelationalOperator;

    const IS = {
      label: i18n.t("query-filter.relational-keywords.is"),
      value: "IS",
    } as FieldRelationalOperator;

    const IS_NOT = {
      label: i18n.t("query-filter.relational-keywords.is-not"),
      value: "IS NOT",
    } as FieldRelationalOperator;

    const IN = {
      label: i18n.t("query-filter.relational-keywords.is-one-of"),
      value: "IN",
    } as FieldRelationalOperator;

    const NOT_IN = {
      label: i18n.t("query-filter.relational-keywords.is-not-one-of"),
      value: "NOT IN",
    } as FieldRelationalOperator;

    const CONTAINS_ALL = {
      label: i18n.t("query-filter.relational-keywords.contains-all-of"),
      value: "CONTAINS ALL",
    } as FieldRelationalOperator;

    const LIKE = {
      label: i18n.t("query-filter.relational-keywords.is-like"),
      value: "LIKE",
    } as FieldRelationalOperator;

    const NOT_LIKE = {
      label: i18n.t("query-filter.relational-keywords.is-not-like"),
      value: "NOT LIKE",
    } as FieldRelationalOperator;

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
  });

  const placeholderKeywords = computed<Record<PlaceholderKeyword, FieldPlaceholderKeyword>>(() => {
    const NOW = {
      label: "Now",
      value: "$NOW",
    } as FieldPlaceholderKeyword;

    return {
      $NOW: NOW,
    };
  });

  const relativeDateRelOps = computed<Record<RelationalKeyword | RelationalOperator, FieldRelationalOperator>>(() => {
    const ops = { ...relOps.value };

    ops[">="] = { ...relOps.value[">="], label: i18n.t("query-filter.relational-operators.is-newer-than") };
    ops["<="] = { ...relOps.value["<="], label: i18n.t("query-filter.relational-operators.is-older-than") };

    return ops;
  });

  function getRelOps(fieldType: FieldType): typeof relOps | typeof relativeDateRelOps {
    switch (fieldType) {
      case "relativeDate":
        return relativeDateRelOps;

      default:
        return relOps;
    }
  }

  function isOrganizerType(type: FieldType): type is Organizer {
    return (
      type === Organizer.Category
      || type === Organizer.Tag
      || type === Organizer.Tool
      || type === Organizer.Food
      || type === Organizer.Household
      || type === Organizer.User
    );
  };

  function getFieldFromFieldDef(field: Field | FieldDefinition, resetValue = false): Field {
    const updatedField = {
      logicalOperator: logOps.value.AND,
      ...field,
    } as Field;

    let operatorChoices: FieldRelationalOperator[];
    if (updatedField.fieldChoices?.length || isOrganizerType(updatedField.type)) {
      operatorChoices = [
        relOps.value["IN"],
        relOps.value["NOT IN"],
        relOps.value["CONTAINS ALL"],
      ];
    }
    else {
      switch (updatedField.type) {
        case "string":
          operatorChoices = [
            relOps.value["="],
            relOps.value["<>"],
            relOps.value["LIKE"],
            relOps.value["NOT LIKE"],
          ];
          break;
        case "number":
          operatorChoices = [
            relOps.value["="],
            relOps.value["<>"],
            relOps.value[">"],
            relOps.value[">="],
            relOps.value["<"],
            relOps.value["<="],
          ];
          break;
        case "boolean":
          operatorChoices = [relOps.value["="]];
          break;
        case "date":
          operatorChoices = [
            relOps.value["="],
            relOps.value["<>"],
            relOps.value[">"],
            relOps.value[">="],
            relOps.value["<"],
            relOps.value["<="],
          ];
          break;
        case "relativeDate":
          operatorChoices = [
            // "<=" is first since "older than" is the most common operator
            relativeDateRelOps.value["<="],
            relativeDateRelOps.value[">="],
          ];
          break;
        default:
          operatorChoices = [relOps.value["="], relOps.value["<>"]];
      }
    }
    updatedField.relationalOperatorChoices = operatorChoices;
    if (!operatorChoices.includes(updatedField.relationalOperatorValue)) {
      updatedField.relationalOperatorValue = operatorChoices[0];
    }

    if (resetValue) {
      updatedField.value = "";
      updatedField.values = [];
      updatedField.organizers = [];
    }
    else {
      updatedField.value = updatedField.value || "";
      updatedField.values = updatedField.values || [];
      updatedField.organizers = updatedField.organizers || [];
    }

    return updatedField;
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
      }
      else {
        isValid = false;
      }

      if (field.relationalOperatorValue) {
        parts.push(field.relationalOperatorValue.value);
      }
      else if (field.type !== "boolean") {
        isValid = false;
      }

      if (field.fieldChoices?.length || isOrganizerType(field.type)) {
        if (field.values?.length) {
          let val: string;
          if (field.type === "string" || field.type === "date" || isOrganizerType(field.type)) {
            val = field.values.map(value => `"${value.toString()}"`).join(",");
          }
          else {
            val = field.values.join(",");
          }
          parts.push(`[${val}]`);
        }
        else {
          isValid = false;
        }
      }
      else if (field.value) {
        if (field.type === "string" || field.type === "date") {
          parts.push(`"${field.value.toString()}"`);
        }
        else {
          parts.push(field.value.toString());
        }
      }
      else if (field.type === "boolean") {
        parts.push("false");
      }
      else {
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
    placeholderKeywords,
    getRelOps,
    buildQueryFilterString,
    getFieldFromFieldDef,
    isOrganizerType,
  };
}
