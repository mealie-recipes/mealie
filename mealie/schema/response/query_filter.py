from __future__ import annotations

import re
from collections import deque
from enum import Enum
from typing import Any, TypeVar, cast
from uuid import UUID

from dateutil import parser as date_parser
from dateutil.parser import ParserError
from humps import decamelize
from sqlalchemy import ColumnElement, Select, and_, inspect, or_
from sqlalchemy.ext.associationproxy import AssociationProxyInstance
from sqlalchemy.orm import InstrumentedAttribute, Mapper
from sqlalchemy.sql import sqltypes

from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID

Model = TypeVar("Model", bound=SqlAlchemyBase)


class RelationalKeyword(Enum):
    IS = "IS"
    IS_NOT = "IS NOT"
    IN = "IN"
    NOT_IN = "NOT IN"
    CONTAINS_ALL = "CONTAINS ALL"
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

        # validate relationship/value pairs
        if relationship in [
            RelationalKeyword.IN,
            RelationalKeyword.NOT_IN,
            RelationalKeyword.CONTAINS_ALL,
        ] and not isinstance(value, list):
            raise ValueError(
                f"invalid query string: {relationship.value} must be given a list of values"
                f"enclosed by {QueryFilter.l_list_sep} and {QueryFilter.r_list_sep}"
            )

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

    def validate(self, model_attr_type: Any) -> Any:
        """Validate value against an model attribute's type and return a validated value, or raise a ValueError"""

        sanitized_values: list[Any]
        if not isinstance(self.value, list):
            sanitized_values = [self.value]
        else:
            sanitized_values = self.value

        for i, v in enumerate(sanitized_values):
            # always allow querying for null values
            if v is None:
                continue

            if self.relationship is RelationalKeyword.LIKE or self.relationship is RelationalKeyword.NOT_LIKE:
                if not isinstance(model_attr_type, sqltypes.String):
                    raise ValueError(
                        f'invalid query string: "{self.relationship.value}" can only be used with string columns'
                    )

            if isinstance(model_attr_type, (GUID)):
                try:
                    # we don't set value since a UUID is functionally identical to a string here
                    UUID(v)
                except ValueError as e:
                    raise ValueError(f"invalid query string: invalid UUID '{v}'") from e

            if isinstance(model_attr_type, sqltypes.Date | sqltypes.DateTime):
                try:
                    dt = date_parser.parse(v)
                    sanitized_values[i] = dt.date() if isinstance(model_attr_type, sqltypes.Date) else dt
                except ParserError as e:
                    raise ValueError(f"invalid query string: unknown date or datetime format '{v}'") from e

            if isinstance(model_attr_type, sqltypes.Boolean):
                try:
                    sanitized_values[i] = v.lower()[0] in ["t", "y"] or v == "1"
                except IndexError as e:
                    raise ValueError("invalid query string") from e

        return sanitized_values if isinstance(self.value, list) else sanitized_values[0]


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

    @classmethod
    def _consolidate_group(cls, group: list[ColumnElement], logical_operators: deque[LogicalOperator]) -> ColumnElement:
        consolidated_group_builder: ColumnElement | None = None
        for i, element in enumerate(reversed(group)):
            if not i:
                consolidated_group_builder = element
            else:
                operator = logical_operators.pop()
                if operator is LogicalOperator.AND:
                    consolidated_group_builder = and_(consolidated_group_builder, element)
                elif operator is LogicalOperator.OR:
                    consolidated_group_builder = or_(consolidated_group_builder, element)
                else:
                    raise ValueError(f"invalid logical operator {operator}")

            if i == len(group) - 1:
                return consolidated_group_builder.self_group()

    @classmethod
    def get_model_and_model_attr_from_attr_string(
        cls, attr_string: str, model: type[Model], *, query: Select | None = None
    ) -> tuple[SqlAlchemyBase, InstrumentedAttribute, Select | None]:
        """
        Take an attribute string and traverse a database model and its relationships to get the desired
        model and model attribute. Optionally provide a query to apply the necessary table joins.

        If the attribute string is invalid, raises a `ValueError`.

        For instance, the attribute string "user.name" on `RecipeModel`
        will return the `User` model's `name` attribute.

        Works with shallow attributes (e.g. "slug" from `RecipeModel`)
        and arbitrarily deep ones (e.g. "recipe.group.preferences" on `RecipeTimelineEvent`).
        """
        mapper: Mapper
        model_attr: InstrumentedAttribute | None = None

        attribute_chain = attr_string.split(".")
        if not attribute_chain:
            raise ValueError("invalid query string: attribute name cannot be empty")

        current_model: SqlAlchemyBase = model  # type: ignore
        for i, attribute_link in enumerate(attribute_chain):
            try:
                model_attr = getattr(current_model, attribute_link)

                # proxied attributes can't be joined to the query directly, so we need to inspect the proxy
                # and get the actual model and its attribute
                if isinstance(model_attr, AssociationProxyInstance):
                    proxied_attribute_link = model_attr.target_collection
                    next_attribute_link = model_attr.value_attr
                    model_attr = getattr(current_model, proxied_attribute_link)

                    if query is not None:
                        query = query.join(model_attr, isouter=True)

                    mapper = inspect(current_model)
                    relationship = mapper.relationships[proxied_attribute_link]
                    current_model = relationship.mapper.class_
                    model_attr = getattr(current_model, next_attribute_link)

                # at the end of the chain there are no more relationships to inspect
                if i == len(attribute_chain) - 1:
                    break

                if query is not None:
                    query = query.join(model_attr, isouter=True)

                mapper = inspect(current_model)
                relationship = mapper.relationships[attribute_link]
                current_model = relationship.mapper.class_

            except (AttributeError, KeyError) as e:
                raise ValueError(f"invalid attribute string: '{attr_string}' does not exist on this schema") from e

        if model_attr is None:
            raise ValueError(f"invalid attribute string: '{attr_string}'")

        return current_model, model_attr, query

    def filter_query(self, query: Select, model: type[Model]) -> Select:
        # join tables and build model chain
        attr_model_map: dict[int, Any] = {}
        model_attr: InstrumentedAttribute
        for i, component in enumerate(self.filter_components):
            if not isinstance(component, QueryFilterComponent):
                continue

            nested_model, model_attr, query = self.get_model_and_model_attr_from_attr_string(
                component.attribute_name, model, query=query
            )
            attr_model_map[i] = nested_model

        # build query filter
        partial_group: list[ColumnElement] = []
        partial_group_stack: deque[list[ColumnElement]] = deque()
        logical_operator_stack: deque[LogicalOperator] = deque()
        for i, component in enumerate(self.filter_components):
            if component == self.l_group_sep:
                partial_group_stack.append(partial_group)
                partial_group = []

            elif component == self.r_group_sep:
                if partial_group:
                    complete_group = self._consolidate_group(partial_group, logical_operator_stack)
                    partial_group = partial_group_stack.pop()
                    partial_group.append(complete_group)
                else:
                    partial_group = partial_group_stack.pop()

            elif isinstance(component, LogicalOperator):
                logical_operator_stack.append(component)

            else:
                component = cast(QueryFilterComponent, component)
                model_attr = getattr(attr_model_map[i], component.attribute_name.split(".")[-1])

                # Keywords
                if component.relationship is RelationalKeyword.IS:
                    element = model_attr.is_(component.validate(model_attr.type))
                elif component.relationship is RelationalKeyword.IS_NOT:
                    element = model_attr.is_not(component.validate(model_attr.type))
                elif component.relationship is RelationalKeyword.IN:
                    element = model_attr.in_(component.validate(model_attr.type))
                elif component.relationship is RelationalKeyword.NOT_IN:
                    element = model_attr.not_in(component.validate(model_attr.type))
                elif component.relationship is RelationalKeyword.CONTAINS_ALL:
                    primary_model_attr: InstrumentedAttribute = getattr(model, component.attribute_name.split(".")[0])
                    element = and_()
                    for v in component.validate(model_attr.type):
                        element = and_(element, primary_model_attr.any(model_attr == v))
                elif component.relationship is RelationalKeyword.LIKE:
                    element = model_attr.like(component.validate(model_attr.type))
                elif component.relationship is RelationalKeyword.NOT_LIKE:
                    element = model_attr.not_like(component.validate(model_attr.type))

                # Operators
                elif component.relationship is RelationalOperator.EQ:
                    element = model_attr == component.validate(model_attr.type)
                elif component.relationship is RelationalOperator.NOTEQ:
                    element = model_attr != component.validate(model_attr.type)
                elif component.relationship is RelationalOperator.GT:
                    element = model_attr > component.validate(model_attr.type)
                elif component.relationship is RelationalOperator.LT:
                    element = model_attr < component.validate(model_attr.type)
                elif component.relationship is RelationalOperator.GTE:
                    element = model_attr >= component.validate(model_attr.type)
                elif component.relationship is RelationalOperator.LTE:
                    element = model_attr <= component.validate(model_attr.type)
                else:
                    raise ValueError(f"invalid relationship {component.relationship}")

                partial_group.append(element)

        # combine the completed groups into one filter
        while True:
            consolidated_group = self._consolidate_group(partial_group, logical_operator_stack)
            if not partial_group_stack:
                return query.filter(consolidated_group)
            else:
                partial_group = partial_group_stack.pop()
                partial_group.append(consolidated_group)

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
        pattern = "|".join([f"\\b{operator.value}\\b" for operator in LogicalOperator])
        logical_operators = re.compile(f"({pattern})", flags=re.IGNORECASE)

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

                # parse out relational keywords and operators
                # each base_subcomponent has exactly zero or one keyword or operator
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
