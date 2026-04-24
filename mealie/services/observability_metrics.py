from __future__ import annotations

from collections import Counter
from threading import Lock

_LOCK = Lock()

_SCORE_BUCKETS = (0.1, 0.25, 0.5, 0.75, 0.9, 1.0)
_ALPHA_BUCKETS = (0.25, 0.5, 0.75, 1.0)

_request_counts: Counter[str] = Counter()
_error_counts: Counter[str] = Counter()
_score_bucket_counts: Counter[float] = Counter()
_alpha_bucket_counts: Counter[float] = Counter()
_score_sum = 0.0
_score_count = 0
_alpha_sum = 0.0
_alpha_count = 0
_low_confidence_total = 0


def _bucket_key(value: float, buckets: tuple[float, ...]) -> float:
    for bucket in buckets:
        if value <= bucket:
            return bucket
    return buckets[-1]


def record_recommendation_request(
    result: str,
    *,
    scores: list[float] | None = None,
    alpha: float | None = None,
    low_confidence: bool = False,
) -> None:
    global _score_sum, _score_count, _alpha_sum, _alpha_count, _low_confidence_total

    with _LOCK:
        _request_counts[result] += 1

        if scores:
            for score in scores:
                bucket = _bucket_key(float(score), _SCORE_BUCKETS)
                _score_bucket_counts[bucket] += 1
                _score_sum += float(score)
                _score_count += 1

        if alpha is not None:
            alpha_value = max(0.0, min(1.0, float(alpha)))
            bucket = _bucket_key(alpha_value, _ALPHA_BUCKETS)
            _alpha_bucket_counts[bucket] += 1
            _alpha_sum += alpha_value
            _alpha_count += 1

        if low_confidence:
            _low_confidence_total += 1


def record_recommendation_error(stage: str) -> None:
    with _LOCK:
        _error_counts[stage] += 1


def render_prometheus_metrics() -> str:
    with _LOCK:
        lines: list[str] = []

        lines.extend(
            [
                "# HELP mealie_recommendation_requests_total Recommendation requests handled by Mealie.",
                "# TYPE mealie_recommendation_requests_total counter",
            ]
        )
        for result, count in sorted(_request_counts.items()):
            lines.append(f'mealie_recommendation_requests_total{{result="{result}"}} {count}')

        lines.extend(
            [
                "# HELP mealie_recommendation_errors_total Recommendation errors handled by Mealie.",
                "# TYPE mealie_recommendation_errors_total counter",
            ]
        )
        for stage, count in sorted(_error_counts.items()):
            lines.append(f'mealie_recommendation_errors_total{{stage="{stage}"}} {count}')

        lines.extend(
            [
                "# HELP mealie_low_confidence_predictions_total Recommendation responses considered low confidence.",
                "# TYPE mealie_low_confidence_predictions_total counter",
                f"mealie_low_confidence_predictions_total {_low_confidence_total}",
            ]
        )

        lines.extend(
            [
                "# HELP mealie_recommendation_score_bucket Recommendation score histogram.",
                "# TYPE mealie_recommendation_score_bucket histogram",
            ]
        )
        running_total = 0
        for bucket in _SCORE_BUCKETS:
            running_total += _score_bucket_counts.get(bucket, 0)
            lines.append(f'mealie_recommendation_score_bucket{{le="{bucket}"}} {running_total}')
        lines.append(f'mealie_recommendation_score_bucket{{le="+Inf"}} {_score_count}')
        lines.append(f"mealie_recommendation_score_sum {_score_sum}")
        lines.append(f"mealie_recommendation_score_count {_score_count}")

        lines.extend(
            [
                "# HELP mealie_personalization_alpha_bucket Personalization alpha histogram.",
                "# TYPE mealie_personalization_alpha_bucket histogram",
            ]
        )
        running_total = 0
        for bucket in _ALPHA_BUCKETS:
            running_total += _alpha_bucket_counts.get(bucket, 0)
            lines.append(f'mealie_personalization_alpha_bucket{{le="{bucket}"}} {running_total}')
        lines.append(f'mealie_personalization_alpha_bucket{{le="+Inf"}} {_alpha_count}')
        lines.append(f"mealie_personalization_alpha_sum {_alpha_sum}")
        lines.append(f"mealie_personalization_alpha_count {_alpha_count}")

        lines.append("")
        return "\n".join(lines)
