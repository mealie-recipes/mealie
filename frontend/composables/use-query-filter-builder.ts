import { computed, useContext } from "@nuxtjs/composition-api";
import { LogicalOperator, RelationalKeyword, RelationalOperator } from "~/lib/api/types/response";

export interface FieldLogicalOperator {
  label: string;
  value: LogicalOperator;
}

export interface FieldRelationalOperator {
  label: string;
  value: RelationalKeyword | RelationalOperator;
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
      "AND": AND,
      "OR": OR,
    };
  });

  const relOps = computed<Record<RelationalKeyword | RelationalOperator, FieldRelationalOperator>>(() => {
    const EQ = {
      label: "=",
      value: "=",
    } as FieldRelationalOperator;

    const NOT_EQ = {
      label: "<>",
      value: "<>",
    } as FieldRelationalOperator;

    const GT = {
      label: ">",
      value: ">",
    } as FieldRelationalOperator;

    const GTE = {
      label: ">=",
      value: ">=",
    } as FieldRelationalOperator;

    const LT = {
      label: "<",
      value: "<",
    } as FieldRelationalOperator;

    const LTE = {
      label: "<=",
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
      label: i18n.tc("query-filter.relational-keywords.in"),
      value: "IN",
    } as FieldRelationalOperator;

    const NOT_IN = {
      label: i18n.tc("query-filter.relational-keywords.not-in"),
      value: "NOT IN",
    } as FieldRelationalOperator;

    const CONTAINS_ALL = {
      label: i18n.tc("query-filter.relational-keywords.contains-all"),
      value: "CONTAINS ALL",
    } as FieldRelationalOperator;

    const LIKE = {
      label: i18n.tc("query-filter.relational-keywords.like"),
      value: "LIKE",
    } as FieldRelationalOperator;

    const NOT_LIKE = {
      label: i18n.tc("query-filter.relational-keywords.not-like"),
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

  return {
    logOps,
    relOps,
  };
}
