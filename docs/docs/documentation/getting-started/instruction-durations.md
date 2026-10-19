# Optional instruction durations

Recipe instruction objects accept `durationSeconds`: either `null` (unspecified)
or a positive whole number of seconds, up to 2147483647. Missing values default
to `null`; numeric zero is normalized to `null` for compatibility. Booleans,
strings, fractional seconds, negative values and out-of-range values are
rejected. Whole JSON numbers such as `1`, `1.0` and `1e0` are equivalent.

```json
{"text": "Let the dough rest", "durationSeconds": 90}
```

The always-visible editor labels the optional field **Duration (minutes)** and
accepts whole minutes only, from 0 to 35791394. For example, entering `2` minutes
stores 120 seconds. Clearing the field (or entering zero) removes the duration.
Viewing or opening an empty field does not assign a time. Imported seconds that
are not an exact number of minutes remain unchanged on unrelated edits. The
editor shows their whole-minute portion and an exact saved-duration hint; editing
the field deliberately replaces that duration with whole minutes. Read-only
instructions show hours, minutes and seconds. A duration does not start a timer
or introduce an external service dependency.

The nullable integer database column follows the seconds-based storage introduced
for recipe times in #8539. Maintainer review selected seconds storage with a
whole-minute, always-visible editor; sub-minute editing is not supported.

The additive Alembic migration follows `a91720b8a7e7`. Existing instructions receive
NULL without changing recipe content. Downgrade removes this new column and
therefore loses instruction durations; other recipe data is retained. Previously
unmerged experimental `cook_time` / `duration_minutes` schemas are not supported
upgrade paths. Native raw JSON export and ZIP import preserve exact seconds.

This continues miah120's backend and frontend work in #8001, with their author
commits retained. Follow-up implementation and tests were AI-assisted using
Hermes (OpenAI model); final review and publication remain with the contributor.
