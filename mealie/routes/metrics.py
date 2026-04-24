from fastapi import APIRouter
from starlette.responses import Response

from mealie.services.observability_metrics import render_prometheus_metrics

router = APIRouter(prefix="/metrics", tags=["Metrics"], include_in_schema=False)


@router.get("")
def metrics() -> Response:
    return Response(render_prometheus_metrics(), media_type="text/plain; version=0.0.4")
