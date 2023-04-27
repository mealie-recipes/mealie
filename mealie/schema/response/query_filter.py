from __future__ import annotations

import datetime
import re
from enum import Enum
from typing import Any, TypeVar, cast
from uuid import UUID

from dateutil import parser as date_parser
from dateutil.parser import ParserError
from humps import decamelize
from sqlalchemy import Select, bindparam, inspect, text
from sqlalchemy.orm import Mapper
from sqlalchemy.sql import sqltypes
from sqlalchemy.sql.expression import BindParameter

from mealie.db.models._model_utils.guid import GUID

Model = TypeVar("Model")


class RelationalKeyword(Enum):
    IS = "IS"
    IS_NOT = "IS NOT"
    IN = "IN"
    NOT_IN = "NOT IN"
    LIKE = "LIKE"
    NOT_LIKE = "NOT LIKE"

    @classmethod
    def parse_component(cls, component: str) -> list[str] | None:
        """
        Try to parse a component using a relational keyword

        If no matching keyword is found, returns None
        """

        # extract the attribute name from the component
        parsed_component = component.split(maxsplit=1)
        if len(parsed_component) < 2:
            return None

        # assume the component has already filtered out the value and try to match a keyword
        # if we try to filter out the value without checking first, keywords with spaces won't parse correctly
        possible_keyword = parsed_component[1].strip().lower()
        for rel_kw in sorted([keyword.value for keyword in cls], key=len, reverse=True):
            if rel_kw.lower() != possible_keyword:
                continue

            parsed_component[1] = rel_kw
            return parsed_component

        # there was no match, so the component may still have the value in it
        try:
            _possible_keyword, _value = parsed_component[-1].rsplit(maxsplit=1)
            parsed_component = [parsed_component[0], _possible_keyword, _value]
        except ValueError:
            # the component has no value to filter out
            return None

        possible_keyword = parsed_component[1].strip().lower()
        for rel_kw in sorted([keyword.value for keyword in cls], key=len, reverse=True):
            if rel_kw.lower() != possible_keyword:
                continue

            parsed_component[1] = rel_kw
            return parsed_component

        return None


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


class LogicalOperator(Enum):
    AND = "AND"
    OR = "OR"


class QueryFilterComponent:
    """A single relational statement"""

    @staticmethod
    def strip_quotes_from_string(val: str) -> str:
        if len(val) > 2 and val[0] == '"' and val[-1] == '"':
            return val[1:-1]
        else:
            return val

    def __init__(
        self, attribute_name: str, relationship: RelationalKeyword | RelationalOperator, value: str | list[str]
    ) -> None:
        self.attribute_name = decamelize(attribute_name)
        self.relationship = relationship

        # remove encasing quotes
        if isinstance(value, str):
            value = self.strip_quotes_from_string(value)

        elif isinstance(value, list):
            value = [self.strip_quotes_from_string(v) for v in value]

        if relationship is RelationalKeyword.IS or relationship is RelationalKeyword.IS_NOT:
            if not isinstance(value, str) or value.lower() not in ["null", "none"]:
                raise ValueError(
                    f'invalid query string: "{relationship.value}" can only be used with "NULL", not "{value}"'
                )

            self.value = None
        else:
            self.value = value

    def __repr__(self) -> str:
        return f"[{self.attribute_name} {self.relationship.value} {self.value}]"


class QueryFilter:
    l_group_sep: str = "("
    r_group_sep: str = ")"
    group_seps: set[str] = {l_group_sep, r_group_sep}

    l_list_sep: str = "["
    r_list_sep: str = "]"
    list_item_sep: str = ","

    def __init__(self, filter_string: str) -> None:
        # parse filter string
        components = QueryFilter._break_filter_string_into_components(filter_string)
        base_components = QueryFilter._break_components_into_base_components(components)
        if base_components.count(QueryFilter.l_group_sep) != base_components.count(QueryFilter.r_group_sep):
            raise ValueError("invalid query string: parenthesis are unbalanced")

        # parse base components into a filter group
        self.filter_components = QueryFilter._parse_base_components_into_filter_components(base_components)

    def __repr__(self) -> str:
        joined = " ".join(
            [
                str(component.value if isinstance(component, LogicalOperator) else component)
                for component in self.filter_components
            ],
        )

        return f"<<{joined}>>"

    def filter_query(self, query: Select, model: type[Model]) -> Select:
        segments: list[str] = []
        params: list[BindParameter] = []
        for i, component in enumerate(self.filter_components):
            if component in QueryFilter.group_seps:
                segments.append(component)  # type: ignore
                continue

            if isinstance(component, LogicalOperator):
                segments.append(component.value)
                continue

            # for some reason typing doesn't like the lsep and rsep literals, so
            # we explicitly mark this as a filter component instead cast doesn't
            # actually do anything at runtime
            component = cast(QueryFilterComponent, component)
            attribute_chain = component.attribute_name.split(".")
            if not attribute_chain:
                raise ValueError("invalid query string: attribute name cannot be empty")

            attr_model: Any = model
            for j, attribute_link in enumerate(attribute_chain):
                # last element
                if j == len(attribute_chain) - 1:
                    if not hasattr(attr_model, attribute_link):
                        raise ValueError(
                            f"invalid query string: '{component.attribute_name}' does not exist on this schema"
                        )

                    attr_value = attribute_link
                    if j:
                        # use the nested table name, rather than the dot notation
                        component.attribute_name = f"{attr_model.__table__.name}.{attr_value}"

                    continue

                # join on nested model
                try:
                    query = query.join(getattr(attr_model, attribute_link))

                    mapper: Mapper = inspect(attr_model)
                    relationship = mapper.relationships[attribute_link]
                    attr_model = relationship.mapper.class_

                except (AttributeError, KeyError) as e:
                    raise ValueError(
                        f"invalid query string: '{component.attribute_name}' does not exist on this schema"
                    ) from e

            # convert values to their proper types
            attr = getattr(attr_model, attr_value)
            values: list[Any]
            if component.relationship in [RelationalKeyword.IN, RelationalKeyword.NOT_IN]:
                if not isinstance(component.value, list):
                    raise ValueError(
                        (
                            f"invalid query string: {component.relationship.value} must be given a list of values"
                            f"enclosed by {QueryFilter.l_list_sep} and {QueryFilter.r_list_sep}"
                        )
                    )
                values = component.value
            else:
                values = [component.value]

            # validate values against model attr type bindings
            for j, v in enumerate(values):
                # always allow querying for null values
                if v is None:
                    continue

                if (
                    component.relationship is RelationalKeyword.LIKE
                    or component.relationship is RelationalKeyword.NOT_LIKE
                ):
                    if not isinstance(attr.type, sqltypes.String):
                        raise ValueError(
                            f'invalid query string: "{component.relationship.value}" can only be used with string columns'
                        )

                if isinstance(attr.type, (GUID)):
                    try:
                        # we don't set value since a UUID is functionally identical to a string here
                        UUID(v)
                    except ValueError as e:
                        raise ValueError(f"invalid query string: invalid UUID '{v}'") from e

                if isinstance(attr.type, (sqltypes.Date, sqltypes.DateTime)):
                    try:
                        values[j] = date_parser.parse(v)
                    except ParserError as e:
                        raise ValueError(f"invalid query string: unknown date or datetime format '{v}'") from e

                if isinstance(attr.type, sqltypes.Boolean):
                    try:
                        values[j] = v.lower()[0] in ["t", "y"] or v == "1"
                    except IndexError as e:
                        raise ValueError("invalid query string") from e

            paramkey = f"P{i+1}"
            paramvalue = values if isinstance(component.value, list) else values[0]
            segments.append(" ".join([component.attribute_name, component.relationship.value, f":{paramkey}"]))
            params.append(bindparam(paramkey, paramvalue, attr.type, expanding=isinstance(component.value, list)))

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
                if component in QueryFilter.group_seps:
                    subcomponents.append(component)
                    continue

                # construct a component until it hits the right separator
                new_component = ""
                for c in component:
                    # ignore characters in-between quotes
                    if c == '"':
                        in_quotes = not in_quotes

                    if c in QueryFilter.group_seps and not in_quotes:
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
    def _break_components_into_base_components(components: list[str]) -> list[str | list[str]]:
        """Further break down components by splitting at relational and logical operators"""
        logical_operators = re.compile(
            f'({"|".join(operator.value for operator in LogicalOperator)})', flags=re.IGNORECASE
        )

        in_list = False
        base_components: list[str | list] = []
        list_value_components = []
        for component in components:
            # parse out lists as their own singular sub component
            subcomponents = component.split(QueryFilter.l_list_sep)
            for i, subcomponent in enumerate(subcomponents):
                if not i:
                    continue

                for j, list_value_string in enumerate(subcomponent.split(QueryFilter.r_list_sep)):
                    if j % 2:
                        continue

                    list_value_components.append(
                        [val.strip() for val in list_value_string.split(QueryFilter.list_item_sep)]
                    )

            quote_offset = 0
            subcomponents = component.split('"')
            for i, subcomponent in enumerate(subcomponents):
                # we are in a list subcomponent, which is already handled
                if in_list:
                    if QueryFilter.r_list_sep in subcomponent:
                        # filter out the remainder of the list subcomponent and continue parsing
                        base_components.append(list_value_components.pop(0))
                        subcomponent = subcomponent.split(QueryFilter.r_list_sep, maxsplit=1)[-1].strip()
                        in_list = False
                    else:
                        continue

                # don't parse components comprised of only a separator
                if subcomponent in QueryFilter.group_seps:
                    quote_offset += 1
                    base_components.append(subcomponent)
                    continue

                # this subcomponent was surrounded in quotes, so we keep it as-is
                if (i + quote_offset) % 2:
                    base_components.append(f'"{subcomponent.strip()}"')
                    continue

                # if the final subcomponent has quotes, it creates an extra empty subcomponent at the end
                if not subcomponent:
                    continue

                # continue parsing this subcomponent up to the list, then skip over subsequent subcomponents
                if not in_list and QueryFilter.l_list_sep in subcomponent:
                    subcomponent, _new_sub_component = subcomponent.split(QueryFilter.l_list_sep, maxsplit=1)
                    subcomponent = subcomponent.strip()
                    subcomponents.insert(i + 1, _new_sub_component)
                    quote_offset += 1
                    in_list = True

                # parse out logical operators
                new_components = [
                    base_component.strip() for base_component in logical_operators.split(subcomponent) if base_component
                ]

                # parse out relational keywords and operators; each base_subcomponent has exactly zero or one keyword or operator
                for component in new_components:
                    if not component:
                        continue

                    # we try relational operators first since they aren't required to be surrounded by spaces
                    parsed_component = RelationalOperator.parse_component(component)
                    if parsed_component is not None:
                        base_components.extend(parsed_component)
                        continue

                    parsed_component = RelationalKeyword.parse_component(component)
                    if parsed_component is not None:
                        base_components.extend(parsed_component)
                        continue

                    # this component does not have any keywords or operators, so we just add it as-is
                    base_components.append(component)

        return base_components

    @staticmethod
    def _parse_base_components_into_filter_components(
        base_components: list[str | list[str]],
    ) -> list[str | QueryFilterComponent | LogicalOperator]:
        """Walk through base components and construct filter collections"""
        relational_keywords = [kw.value for kw in RelationalKeyword]
        relational_operators = [op.value for op in RelationalOperator]
        logical_operators = [op.value for op in LogicalOperator]

        # parse QueryFilterComponents and logical operators
        components: list[str | QueryFilterComponent | LogicalOperator] = []
        for i, base_component in enumerate(base_components):
            if isinstance(base_component, list):
                continue

            if base_component in QueryFilter.group_seps:
                components.append(base_component)

            elif base_component in relational_keywords or base_component in relational_operators:
                relationship: RelationalKeyword | RelationalOperator
                if base_component in relational_keywords:
                    relationship = RelationalKeyword(base_components[i])
                else:
                    relationship = RelationalOperator(base_components[i])

                components.append(
                    QueryFilterComponent(
                        attribute_name=base_components[i - 1],  # type: ignore
                        relationship=relationship,
                        value=base_components[i + 1],
                    )
                )

            elif base_component.upper() in logical_operators:
                components.append(LogicalOperator(base_component.upper()))

        return components
