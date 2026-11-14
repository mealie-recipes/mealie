# Recipe Search

Recipe search matches titles, descriptions, ingredient text, and structured ingredient food names.
By default, a recipe must match every search concept.
For example, `pork lettuce wrap` matches pork lettuce cups through a small list of culinary equivalents.
It does not match a recipe that mentions only pork.

| Syntax | Example | Result |
| --- | --- | --- |
| Ordinary words | `pork lettuce wrap` | Match all concepts, with supported synonyms and conservative typo correction. |
| Double quotes | `"lettuce cups" pork` | Require the exact phrase and the pork concept. |
| Required literal word | `+pork lettuce wrap` | Require the whole word pork, even after you broaden the search. |
| Excluded word | `pork -cilantro` | Exclude recipes that mention the whole word cilantro. |
| Excluded phrase | `pork -"chili peppers"` | Exclude recipes that contain the exact phrase. |

Search ignores case, accents, and punctuation. Phrases must stay within one field or ingredient line.
A single ordinary term also matches word prefixes. For example, `chick` can find chicken.
Quoted phrases and signed terms do not use synonyms, typo correction, or prefix matches.
Search keeps non-Latin words in their original script.

Select **Broaden Search** to accept partial concept matches.
Broad search retains quoted phrases, `+` requirements, and `-` exclusions.
Select **Show Strong Matches** to require all concepts again.
A new query restores strong matches.

Results use relevance first. Other sort choices break relevance ties.
The supported syntax does not include Boolean `OR` or parentheses.
Exclusions check recorded text; they do not guarantee that an ingredient or allergen is absent.

## API

Authenticated and public recipe-list endpoints accept `search` and `searchMode`.
`searchMode=all` is the default; `searchMode=any` enables broad search.
Encode a literal `+` as `%2B` in URLs.
The pagination response keeps its existing shape and exact totals.
Search accepts up to 512 characters and 32 clauses.
Unmatched double quotes and empty signed terms return a validation error.

## Search Index Maintenance

Database migrations create and populate search indexes.
Recipe and food changes update the indexes within the source transaction.
Backups omit derived search data; restore rebuilds it from the source records.

To rebuild the indexes manually, run this command in the configured backend environment:

```sh
uv run python -m mealie.search.rebuild
```

The rebuild can block concurrent writes. Use a maintenance window for large libraries.
