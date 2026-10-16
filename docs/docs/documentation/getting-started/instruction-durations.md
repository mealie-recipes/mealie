# Optional instruction durations

Recipe instruction objects accept `durationSeconds`: either `null` (unspecified)
or a positive whole number of seconds, up to 2147483647. Missing values default
to `null`; numeric zero is normalized to `null` for compatibility. Booleans,
strings, fractional seconds, negative values and out-of-range values are
rejected. Whole JSON numbers such as `1`, `1.0` and `1e0` are equivalent.

```json
{"text": "Let the dough rest", "durationSeconds": 90}
```

The editor labels the field **Duration (minutes)**. For example, entering `1.5`
minutes stores 90 seconds. Clearing the field removes the duration. Viewing or
opening an empty field does not assign a time. Read-only instructions show units
(hours, minutes and seconds) rather than an ambiguous `0:00`. A duration does not
start a timer or introduce an external service dependency.

The nullable integer database column follows the seconds-based storage introduced
for recipe times in #8539. This is a proposal, not a claim that the maintainers
have selected instruction-duration units: earlier review of #8001 preferred
integer minutes. Maintainers still need to approve seconds storage/minutes input,
fractional-minute entry for exact seconds, and one of the two mutually exclusive
editor presentations (always-visible field or **Add time** disclosure).

The additive Alembic migration follows `27621d27c7e1`. Existing instructions receive
NULL without changing recipe content. Downgrade removes this new column and
therefore loses instruction durations; other recipe data is retained. Previously
unmerged experimental `cook_time` / `duration_minutes` schemas are not supported
upgrade paths. Native raw JSON export and ZIP import preserve exact seconds.

This continues miah120's backend and frontend work in #8001, with their author
commits retained. Follow-up implementation and tests were AI-assisted using
Hermes (OpenAI model); final review and publication remain with the contributor.
