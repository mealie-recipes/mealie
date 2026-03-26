from enum import Enum


class LogicalOperator(Enum):
    AND = "AND"
    OR = "OR"


class RelationalOperator(Enum):
    EQ = "="
    NOTEQ = "<>"
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="

    @classmethod
    def parse_component(cls, component: str) -> list[str] | None:
        """
        Try to parse a component using a relational operator

        If no matching operator is found, returns None
        """

        for rel_op in sorted([operator.value for operator in cls], key=len, reverse=True):
            if rel_op not in component:
                continue

            parsed_component = [base_component.strip() for base_component in component.split(rel_op) if base_component]
            parsed_component.insert(1, rel_op)
            return parsed_component

        return None
