"""Compile the shared recipe search policy to indexed SQL."""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import Select
from sqlalchemy.orm import Session

from mealie.db.models.recipe.recipe import RecipeModel

from .index import segments, terms
from .query import Clause, SearchMode, correction, parse


def _matches(session: Session, value: str, prefix: bool = False) -> Select:
    return _match_any(session, (value,), prefix)


def _match_any(session: Session, values: Sequence[str], prefix: bool = False) -> Select:
    if session.get_bind().dialect.name == "sqlite":
        expression = " OR ".join('"' + value + '"' + ("*" if prefix else "") for value in values)
        return sa.select(segments.c.recipe_id, segments.c.field).where(
            sa.literal_column("recipe_search_segments.rowid").in_(
                sa.select(sa.literal_column("rowid"))
                .select_from(sa.table("recipe_search_fts"))
                .where(sa.literal_column("recipe_search_fts").op("MATCH")(expression))
            )
        )
    expression = " | ".join(
        "(" + " <-> ".join("'" + token + "'" for token in value.split()) + (":*" if prefix else "") + ")"
        for value in values
    )
    return sa.select(segments.c.recipe_id, segments.c.field).where(
        sa.literal_column("document").op("@@")(sa.func.to_tsquery(sa.literal_column("'simple'"), expression))
    )


def _alternatives(session: Session, clause: Clause, visible: Select, prefix: bool) -> Sequence[str]:
    alternatives = clause.alternatives
    if clause.kind != "ordinary" or " " in clause.text or len(clause.text) < 5:
        return alternatives
    existing = _match_any(session, alternatives, prefix).subquery()
    if session.scalar(sa.select(sa.exists().where(existing.c.recipe_id.in_(visible)))):
        return alternatives
    vocabulary = set(
        session.scalars(
            sa.select(terms.c.term)
            .where(
                terms.c.recipe_id.in_(visible),
                terms.c.length.between(len(clause.text) - 1, len(clause.text) + 1),
            )
            .distinct()
        )
    )
    fixed = correction(clause.text, vocabulary)
    return (*alternatives, fixed) if fixed else alternatives


def prepare_search(
    session: Session, query: Select, search: str, mode: SearchMode = "all"
) -> tuple[Select, Select | None]:
    parsed = parse(search, mode)
    if not parsed.clauses:
        return query, None
    visible_ids = (query.order_by(None).with_only_columns(sa.cast(RecipeModel.id, sa.Text).label("recipe_id"))).cte(
        "search_visible"
    )
    visible = sa.select(visible_ids.c.recipe_id)
    positive: list[tuple[int, Clause]] = []
    exclusions: list[Select] = []
    selections: list[Select] = []
    for number, clause in enumerate(parsed.clauses):
        if clause.kind == "excluded":
            exclusions.append(_matches(session, clause.text).with_only_columns(segments.c.recipe_id))
            continue
        positive.append((number, clause))
        prefix = parsed.prefix and clause.kind == "ordinary"
        alternatives = _alternatives(session, clause, visible, prefix)
        if prefix and alternatives == clause.alternatives:
            alternatives = (clause.text,)
        elif prefix:
            prefix = False
        matches = _match_any(session, alternatives, prefix).where(segments.c.recipe_id.in_(visible))
        literal = sa.literal(1)
        if len(alternatives) > 1:
            literal_ids = _matches(session, clause.text, prefix).with_only_columns(segments.c.recipe_id)
            literal = sa.case((segments.c.recipe_id.in_(literal_ids), 1), else_=0)
        selections.append(matches.add_columns(sa.literal(number).label("clause"), literal.label("literal")))
    recipe_id = sa.cast(RecipeModel.id, sa.Text)
    for excluded in exclusions:
        query = query.where(recipe_id.not_in(excluded))
    if not positive:
        return query, None
    hits = (sa.union_all(*selections) if len(selections) > 1 else selections[0]).cte("search_raw_hits")
    if exclusions:
        retained = sa.select(hits)
        for excluded in exclusions:
            retained = retained.where(hits.c.recipe_id.not_in(excluded))
        hits = retained.cte("search_hits")
    mandatory = [number for number, clause in positive if clause.kind != "ordinary" or mode == "all"]
    ordinary = [number for number, clause in positive if clause.kind == "ordinary"]
    eligibility = (
        sa.select(hits.c.recipe_id)
        .group_by(hits.c.recipe_id)
        .having(sa.func.count(sa.distinct(sa.case((hits.c.clause.in_(mandatory), hits.c.clause)))) == len(mandatory))
    )
    if mode == "any" and ordinary:
        eligibility = eligibility.having(sa.func.count(sa.case((hits.c.clause.in_(ordinary), 1))) > 0)
    eligible = eligibility.cte("search_eligible")
    count_rows = sa.select(eligible.c.recipe_id)
    for excluded in exclusions:
        count_rows = count_rows.where(eligible.c.recipe_id.not_in(excluded))
    count_query = sa.select(sa.func.count()).select_from(count_rows.subquery())
    if len(positive) == 1:
        ranked = sa.select(
            hits.c.recipe_id,
            sa.literal(1).label("coverage"),
            sa.func.max(sa.case((hits.c.field == 0, 1), else_=0)).label("title"),
            sa.func.max(sa.case((hits.c.field == 1, 1), else_=0)).label("description"),
            sa.func.max(sa.case((hits.c.field == 2, 1), else_=0)).label("ingredient"),
            sa.func.max(hits.c.literal).label("literal"),
        ).group_by(hits.c.recipe_id)
    else:
        ranked = (
            sa.select(
                hits.c.recipe_id,
                sa.func.count(sa.distinct(hits.c.clause)).label("coverage"),
                sa.func.count(sa.distinct(sa.case((hits.c.field == 0, hits.c.clause)))).label("title"),
                sa.func.count(sa.distinct(sa.case((hits.c.field == 1, hits.c.clause)))).label("description"),
                sa.func.count(sa.distinct(sa.case((hits.c.field == 2, hits.c.clause)))).label("ingredient"),
                sa.func.count(sa.distinct(sa.case((hits.c.literal == 1, hits.c.clause)))).label("literal"),
            )
            .group_by(hits.c.recipe_id)
            .having(
                sa.func.count(sa.distinct(sa.case((hits.c.clause.in_(mandatory), hits.c.clause)))) == len(mandatory)
            )
        )
        if mode == "any" and ordinary:
            ranked = ranked.having(sa.func.count(sa.case((hits.c.clause.in_(ordinary), 1))) > 0)
    ranks = ranked.add_columns(sa.func.count().over().label("search_total")).cte("search_rank")
    title_phrase = " ".join(clause.text for _, clause in positive)
    phrase_ids = _matches(session, title_phrase).where(segments.c.field == 0).with_only_columns(segments.c.recipe_id)
    result = (
        query.add_columns(ranks.c.search_total)
        .join(ranks, RecipeModel.id == sa.cast(ranks.c.recipe_id, RecipeModel.id.type))
        .order_by(
            sa.desc(ranks.c.coverage == len(positive)),
            sa.desc(recipe_id.in_(phrase_ids)),
            sa.desc(ranks.c.title),
            sa.desc(ranks.c.description),
            sa.desc(ranks.c.ingredient),
            sa.desc(ranks.c.literal),
        )
    )
    return result, count_query


def apply_search(session: Session, query: Select, search: str, mode: SearchMode = "all") -> Select:
    return prepare_search(session, query, search, mode)[0]
