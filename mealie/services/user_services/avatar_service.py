import asyncio
import hashlib
import shutil
from urllib.parse import urlparse
from uuid import uuid4

from pydantic import UUID4
from sqlalchemy.orm.session import Session

from mealie.core.dependencies import get_temporary_path
from mealie.core.root_logger import get_logger
from mealie.pkgs import cache, img, safehttp
from mealie.repos.all_repositories import get_repositories
from mealie.schema.user import PrivateUser

logger = get_logger("avatar_service")

# Avatars are downscaled to a small webp thumbnail anyway, so anything beyond this is either a
# mistake on the provider's side or an attempt to exhaust our disk/memory.
MAX_AVATAR_BYTES = 5 * 1024 * 1024

# `resilient_fetch` is built for scraping and will happily spend its full retry budget on a
# stalling host. A login is waiting on this, so cap it well below that budget.
AVATAR_FETCH_TIMEOUT = 10


async def sync_avatar_from_url(session: Session, user_id: UUID4, url: str) -> None:
    """
    Downloads the image at ``url`` and stores it as ``user_id``'s profile image.

    The URL originates from an identity provider's claim, so it is treated as untrusted input:
    it is fetched through ``safehttp``, which rejects non-public target IPs (SSRF) and caps the
    response body. Any failure is logged and swallowed -- a broken avatar must never block a
    login that has otherwise already succeeded.

    The claim's digest is stored alongside the user, so an unchanged URL costs nothing on the
    next login.
    """
    if urlparse(url).scheme != "https":
        logger.warning("[OIDC] refusing to fetch profile image over a non-HTTPS URL")
        return

    repos = get_repositories(session, group_id=None, household_id=None)
    user = repos.users.get_one(user_id)
    if user is None:
        return

    url_hash = hashlib.sha256(url.encode()).hexdigest()
    if user.oidc_picture_hash == url_hash:
        logger.debug("[OIDC] Profile image claim unchanged, skipping download")
        return

    try:
        # FlareSolverr returns HTML, not image bytes, so it can't serve an image download.
        response = await asyncio.wait_for(
            safehttp.resilient_fetch(url, allow_flaresolverr=False, max_bytes=MAX_AVATAR_BYTES),
            timeout=AVATAR_FETCH_TIMEOUT,
        )
    except Exception as e:
        logger.debug("[OIDC] Could not fetch profile image from picture claim: %s", e)
        return

    if response is None:
        # Every impersonation was rejected, or the server returned an error status.
        logger.debug("[OIDC] Profile image request returned no usable response")
        return

    content_type = response.headers.get("content-type", "")
    if "image" not in content_type:
        logger.debug("[OIDC] Profile image Content-Type %s is not an image", content_type)
        return

    try:
        with get_temporary_path() as temp_path:
            # use a generated uuid and ignore the remote filename so we don't
            # need to worry about sanitizing untrusted inputs.
            temp_img = temp_path.joinpath(str(uuid4()))
            temp_img.write_bytes(response.content)

            minified = img.PillowMinifier.to_webp(temp_img)
            shutil.copyfile(minified, PrivateUser.get_directory(user_id) / "profile.webp")

        repos.users.patch(user_id, {"cache_key": cache.new_key(), "oidc_picture_hash": url_hash})
    except Exception as e:
        logger.debug("[OIDC] Could not store profile image from picture claim: %s", e)
