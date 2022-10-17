from __future__ import annotations

import re
from enum import Enum
from typing import Any, TypeVar, cast

from dateutil import parser as date_parser
from dateutil.parser import ParserError
from humps import decamelize
from sqlalchemy import bindparam, text
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import sqltypes
from sqlalchemy.sql.expression import BindParameter

Model = TypeVar("Model")


class RelationalOperator(Enum):
    EQ = "="
    NOTEQ = "<>"
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="


class LogicalOperator(Enum):
    AND = "AND"
    OR = "OR"


class QueryFilterComponent:
    """A single relational statement"""

    def __init__(self, attribute_name: str, relational_operator: RelationalOperator, value: str) -> None:
        self.attribute_name = decamelize(attribute_name)
        self.relational_operator = relational_operator
        self.value = value

        # remove encasing quotes
        if len(value) > 2 and value[0] == '"' and value[-1] == '"':
            self.value = value[1:-1]

    def __repr__(self) -> str:
        return f"[{self.attribute_name} {self.relational_operator.value} {self.value}]"


class QueryFilter:
    lsep: str = "("
    rsep: str = ")"

    seps: set[str] = {lsep, rsep}

    def __init__(self, filter_string: str) -> None:
        # parse filter string
        components = QueryFilter._break_filter_string_into_components(filter_string)
        base_components = QueryFilter._break_components_into_base_components(components)
        if base_components.count(QueryFilter.lsep) != base_components.count(QueryFilter.rsep):
            raise ValueError("invalid filter string: parenthesis are unbalanced")

        # parse base components into a filter group
        self.filter_components = QueryFilter._parse_base_components_into_filter_components(base_components)

    def __repr__(self) -> str:
        return f'<<{" ".join([str(component.value if isinstance(component, LogicalOperator) else component) for component in self.filter_components])}>>'

    def filter_query(self, query: Query, model: type[Model]) -> Query:
        segments: list[str] = []
        params: list[BindParameter] = []
        for i, component in enumerate(self.filter_components):
            if component in QueryFilter.seps:
                segments.append(component)  # type: ignore
                continue

            if isinstance(component, LogicalOperator):
                segments.append(component.value)
                continue

            # for some reason typing doesn't like the lsep and rsep literals, so we explicitly mark this as a filter component instead
            # cast doesn't actually do anything at runtime
            component = cast(QueryFilterComponent, component)

            if not hasattr(model, component.attribute_name):
                raise ValueError(f"invalid query string: '{component.attribute_name}' does not exist on this schema")

            # convert values to their proper types
            attr = getattr(model, component.attribute_name)
            value: Any = component.value

            if isinstance(attr.type, (sqltypes.Date, sqltypes.DateTime)):
                try:
                    value = date_parser.parse(component.value)

                except ParserError as e:
                    raise ValueError(
                        f"invalid query string: unknown date or datetime format '{component.value}'"
                    ) from e

            if isinstance(attr.type, sqltypes.Boolean):
                try:
                    value = component.value.lower()[0] in ["t", "y"] or component.value == "1"

                except IndexError as e:
                    raise ValueError("invalid query string") from e

            paramkey = f"P{i+1}"
            segments.append(" ".join([component.attribute_name, component.relational_operator.value, f":{paramkey}"]))
            params.append(bindparam(paramkey, value, attr.type))

        qs = text(" ".join(segments)).bindparams(*params)
        query = query.filter(qs)
        return query

    @staticmethod
    def _break_filter_string_into_components(filter_string: str) -> list[str]:
        """Recursively break filter string into components based on parenthesis groupings"""
        components = [filter_string]
        in_quotes = False
        while True:
            subcomponents = []
            for component in components:
                # don't parse components comprised of only a separator
                if component in QueryFilter.seps:
                    subcomponents.append(component)
                    continue

                # construct a component until it hits the right separator
                new_component = ""
                for c in component:
                    # ignore characters in-between quotes
                    if c == '"':
                        in_quotes = not in_quotes

                    if c in QueryFilter.seps and not in_quotes:
                        if new_component:
                            subcomponents.append(new_component)

                        subcomponents.append(c)
                        new_component = ""
                        continue

                    new_component += c

                if new_component:
                    subcomponents.append(new_component.strip())

            if components == subcomponents:
                break

            components = subcomponents

        return components

    @staticmethod
    def _break_components_into_base_components(components: list[str]) -> list[str]:
        """Further break down components by splitting at relational and logical operators"""
        logical_operators = re.compile(
            f'({"|".join(operator.value for operator in LogicalOperator)})', flags=re.IGNORECASE
        )

        base_components = []
        for component in components:
            offset = 0
            subcomponents = component.split('"')
            for i, subcomponent in enumerate(subcomponents):
                # don't parse components comprised of only a separator
                if subcomponent in QueryFilter.seps:
                    offset += 1
                    base_components.append(subcomponent)
                    continue

                # this subscomponent was surrounded in quotes, so we keep it as-is
                if (i + offset) % 2:
                    base_components.append(f'"{subcomponent.strip()}"')
                    continue

                # if the final subcomponent has quotes, it creates an extra empty subcomponent at the end
                if not subcomponent:
                    continue

                # parse out logical operators
                new_components = [
                    base_component.strip() for base_component in logical_operators.split(subcomponent) if base_component
                ]

                # parse out relational operators; each base_subcomponent has exactly zero or one relational operator
                # we do them one at a time in descending length since some operators overlap (e.g. :> and >)
                for component in new_components:
                    if not component:
                        continue

                    added_to_base_components = False
                    for rel_op in sorted([operator.value for operator in RelationalOperator], key=len, reverse=True):
                        if rel_op in component:
                            new_base_components = [
                                base_component.strip() for base_component in component.split(rel_op) if base_component
                            ]
                            new_base_components.insert(1, rel_op)
                            base_components.extend(new_base_components)

                            added_to_base_components = True
                            break

                    if not added_to_base_components:
                        base_components.append(component)

        return base_components

    @staticmethod
    def _parse_base_components_into_filter_components(
        base_components: list[str],
    ) -> list[str | QueryFilterComponent | LogicalOperator]:
        """Walk through base components and construct filter collections"""
        relational_operators = [op.value for op in RelationalOperator]
        logical_operators = [op.value for op in LogicalOperator]

        # parse QueryFilterComponents and logical operators
        components: list[str | QueryFilterComponent | LogicalOperator] = []
        for i, base_component in enumerate(base_components):
            if base_component in QueryFilter.seps:
                components.append(base_component)

            elif base_component in relational_operators:
                components.append(
                    QueryFilterComponent(
                        attribute_name=base_components[i - 1],
                        relational_operator=RelationalOperator(base_components[i]),
                        value=base_components[i + 1],
                    )
                )

            elif base_component.upper() in logical_operators:
                components.append(LogicalOperator(base_component.upper()))

        return components
