import inspect
import json
from typing import Any

from asgiref.sync import async_to_sync
from django.http import HttpResponseBase, StreamingHttpResponse
from pydantic import TypeAdapter
from rest_framework.response import Response as DRFResponse
from rest_framework.views import APIView

from mealie.core.config import get_app_settings
from mealie.http.api import APIRoute, HTTPException, RequestValidationError
from mealie.http.dependencies import RequestContext
from mealie.http.encoding import jsonable_encoder
from mealie.http.requests import Request
from mealie.http.responses import EventSourceResponse, FileResponse, copy_headers


class ControllerView(APIView):
    routes: list[APIRoute] = []

    @property
    def default_response_headers(self) -> dict[str, str]:
        # Allow belongs on method errors and must reflect the selected path.
        return {}

    def handle_request(self, drf_request: Any, **path_params: Any) -> HttpResponseBase:
        from mealie.app import app
        from mealie.http.routing import compile_path

        # Django stops at the first matching path; Mealie's API also needs to
        # consider the method before falling back to a 405 (e.g. api-tokens
        # following /users/{item_id}). Preserve declaration order for full matches.
        route = None
        allowed = set()
        for candidate in app.routes:
            match = compile_path(candidate.path).fullmatch(drf_request.path_info)
            if match:
                allowed.update(candidate.methods)
                if drf_request.method in candidate.methods:
                    route = candidate
                    path_params = match.groupdict()
                    break
        if route is None:
            raise HTTPException(405, "Method Not Allowed", {"Allow": ", ".join(sorted(allowed))})
        self.route = route
        context = RequestContext(Request(drf_request), route, path_params)
        try:
            context.parse_body()
            result = async_to_sync(context.execute)()
            response = self.make_response(result, route, context)
            if isinstance(response, StreamingHttpResponse) and response.is_async:
                original = response.streaming_content

                async def stream() -> Any:
                    try:
                        async for chunk in original:
                            yield chunk
                    finally:
                        await original.aclose()
                        await context.finish()

                response.streaming_content = stream()
                response._resource_closers.append(lambda: async_to_sync(context.finish)())
            else:
                # Keep dependency resources open through download cleanup and background work.
                response._resource_closers.append(lambda: async_to_sync(context.finish)())
            return response
        except BaseException:
            async_to_sync(context.close)()
            raise

    def make_response(self, result: Any, route: APIRoute, context: RequestContext) -> HttpResponseBase:
        if isinstance(result, HttpResponseBase):
            response = result
        elif hasattr(result, "raw_headers") and hasattr(result, "body"):
            # Authlib's outbound OIDC integration creates a small redirect response.
            from mealie.http.responses import Response

            response = Response(result.body, status_code=result.status_code)
            for key, value in result.raw_headers:
                response.headers[key.decode()] = value.decode()
        elif route.response_class is EventSourceResponse:
            response = EventSourceResponse(result, status_code=route.status_code)
        elif route.response_class is FileResponse:
            response = FileResponse(result, status_code=route.status_code)
        else:
            if route.response_model is not None:
                adapter = TypeAdapter(route.response_model)
                validated = adapter.validate_python(result, from_attributes=True)
                data = adapter.dump_python(
                    validated,
                    mode="json",
                    by_alias=route.options.get("response_model_by_alias", True),
                    exclude_unset=route.options.get("response_model_exclude_unset", False),
                    exclude_none=route.options.get("response_model_exclude_none", False),
                    exclude_defaults=route.options.get("response_model_exclude_defaults", False),
                    include=route.options.get("response_model_include"),
                    exclude=route.options.get("response_model_exclude"),
                )
            else:
                data = jsonable_encoder(result)
            response = DRFResponse(data, status=route.status_code)
        copy_headers(context.response, response)
        if route.route_class and getattr(route.route_class, "last_modified", False):
            body = response.data if isinstance(response, DRFResponse) else None
            if body is None and not isinstance(response, DRFResponse) and not response.streaming:
                try:
                    body = json.loads(response.content)
                except ValueError, UnicodeDecodeError:
                    pass
            if isinstance(body, dict) and (modified := body.get("updatedAt")):
                response.headers["last-modified"] = modified
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        if isinstance(response, FileResponse):
            from mealie.http.files import prepare_file_response

            prepare_file_response(response, context.request.drf._request)
        return response

    def handle_exception(self, exc: Exception) -> Any:
        if isinstance(exc, HTTPException):
            return DRFResponse({"detail": jsonable_encoder(exc.detail)}, status=exc.status_code, headers=exc.headers)
        if isinstance(exc, RequestValidationError):
            route = getattr(self, "route", None)
            if route:
                exc.endpoint_ctx = {
                    "file": inspect.getsourcefile(route.endpoint),
                    "line": inspect.getsourcelines(route.endpoint)[1],
                    "function": route.endpoint.__name__,
                    "path": f"{self.request.method} {route.path}",
                }
            settings = get_app_settings()
            if not settings.PRODUCTION or settings.TESTING:
                from mealie.routes.handlers import log_wrapper

                log_wrapper(Request(self.request), exc)
                return DRFResponse(
                    {"status_code": 422, "message": str(exc).replace("\n", " ").replace("   ", " "), "data": None},
                    status=422,
                )
            return DRFResponse({"detail": jsonable_encoder(exc.errors())}, status=422)
        return super().handle_exception(exc)

    get = post = put = patch = delete = head = options = handle_request
