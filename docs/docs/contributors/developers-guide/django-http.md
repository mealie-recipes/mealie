# Django HTTP application

Mealie serves its API with Django REST Framework. SQLAlchemy repositories and
Alembic still own the database; Django's ORM, authentication database, and
migration commands are not used. Pydantic remains the source of request and
response schemas, including the types consumed by Nuxt.

`task py` starts Uvicorn with `mealie.http.asgi:application` on port 9000.
The packaged `mealie` command and Docker entrypoint start the same application.
The ASGI lifespan initializes the SQLAlchemy database through Alembic and starts
Mealie's scheduler. Each worker follows the existing worker configuration.

`mealie/http/settings.py` configures HTTP middleware and DRF parsers/renderers.
Routes in `mealie/routes/` declare their paths, methods, Pydantic schemas, and
controller dependencies through `mealie/http/api.py`. Django URL patterns resolve
to DRF `APIView` subclasses. The request context resolves shared dependencies once
per request, retains resources through streaming and background operations, and
closes SQLAlchemy sessions on completion or errors.

The existing JWT and API token services enforce authentication. Controller and
repository checks retain admin, group, and household boundaries. DRF's default
Django session authentication is disabled because it would introduce a separate
identity database and change existing cookie and bearer contracts.

Integration tests use an HTTPX client over Django's WSGI handler, so existing
HTTP assertions exercise the new implementation. Additional ASGI tests cover the
default deployment application and asynchronous response lifetimes.

Use `task py:check`, `task ui:check`, and `task dev:generate` as before.
Use the ASGI entrypoint in deployments that need SSE and the scheduler; the WSGI
entrypoint is provided for synchronous embedding and does not manage the ASGI
application lifespan.
