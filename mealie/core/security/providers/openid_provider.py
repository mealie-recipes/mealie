import hashlib
import ipaddress
import shutil
import socket
from datetime import timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse
from uuid import uuid4

import requests
from authlib.oidc.core import UserInfo
from pydantic import UUID4
from sqlalchemy.orm.session import Session

from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.core.dependencies import get_temporary_path
from mealie.core.exceptions import MissingClaimException
from mealie.core.security.providers.auth_provider import AuthProvider
from mealie.db.models.users.users import AuthMethod
from mealie.pkgs import cache, img
from mealie.repos.all_repositories import get_repositories
from mealie.schema.user import PrivateUser

# Avatars are downscaled to a small webp thumbnail anyway, so anything past this is either a
# mistake on the provider's side or an attempt to exhaust our disk/memory.
MAX_PICTURE_BYTES = 5 * 1024 * 1024

# Enough for the CDN hand-offs avatar hosts normally use, low enough to bound a redirect loop.
MAX_PICTURE_REDIRECTS = 3


class OpenIDProvider(AuthProvider[UserInfo]):
    """Authentication provider that authenticates a user using a token from OIDC ID token"""

    _logger = root_logger.get_logger("openid_provider")

    def __init__(self, session: Session, data: UserInfo, use_default_groups: bool = False) -> None:
        super().__init__(session, data)
        self.use_default_groups = use_default_groups

    def authenticate(self) -> tuple[str, timedelta] | None:
        """Attempt to authenticate a user given a username and password"""

        settings = get_app_settings()
        claims = self.data
        if not claims:
            self._logger.error("[OIDC] No claims in the id_token")
            raise MissingClaimException()

        # Log all claims for debugging
        self._logger.debug("[OIDC] Received claims:")
        for key, value in claims.items():
            self._logger.debug("[OIDC]   %s: %s", key, value)

        if not self.required_claims.issubset(claims.keys()):
            self._logger.debug(
                "[OIDC] Required claims not present. Expected: %s Actual: %s",
                self.required_claims,
                claims.keys(),
            )
            raise MissingClaimException()

        # Check for empty required claims
        for claim in self.required_claims:
            if not claims.get(claim):
                self._logger.debug("[OIDC] Required claim '%s' is empty", claim)
                raise MissingClaimException()

        # Never trust an unverified email. An IdP that lets a user self-assert an
        # arbitrary, unverified address would otherwise allow that user to match
        # (and log into) another account by claiming its email. When the email is
        # verified, matching an existing account is legitimate account linking.
        # Admins whose IdP does not emit the claim can opt out via this setting.
        if settings.OIDC_REQUIRES_EMAIL_VERIFICATION and not claims.get("email_verified", False):
            self._logger.warning("[OIDC] email_verified claim is missing or false; refusing to authenticate")
            raise MissingClaimException()

        repos = get_repositories(self.session, group_id=None, household_id=None)

        is_admin = False
        if settings.OIDC_REQUIRES_GROUP_CLAIM:
            # We explicitly allow the groups claim to be missing to account for the behaviour of some IdPs:
            # https://github.com/keycloak/keycloak/issues/22340
            # We still log a warning though
            if settings.OIDC_GROUPS_CLAIM not in claims:
                self._logger.warning(
                    "[OIDC] claims did not include a %s claim%s",
                    settings.OIDC_GROUPS_CLAIM,
                    ", using an empty list as default" if self.use_default_groups else "",
                )
            group_claim = claims.get(settings.OIDC_GROUPS_CLAIM, []) or []
            is_admin = settings.OIDC_ADMIN_GROUP in group_claim if settings.OIDC_ADMIN_GROUP else False
            is_valid_user = settings.OIDC_USER_GROUP in group_claim if settings.OIDC_USER_GROUP else True

            if not (is_valid_user or is_admin):
                self._logger.warning(
                    "[OIDC] Successfully authenticated, but user does not have one of the required group(s). \
                    Found: %s - Required (one of): %s",
                    group_claim,
                    [settings.OIDC_USER_GROUP, settings.OIDC_ADMIN_GROUP],
                )
                return None

        user = self.try_get_user(claims.get(settings.OIDC_USER_CLAIM))
        if not user:
            if not settings.OIDC_SIGNUP_ENABLED:
                self._logger.debug("[OIDC] No user found. Not creating a new user - new user creation is disabled.")
                return None

            self._logger.debug("[OIDC] No user found. Creating new OIDC user.")

            try:
                # some IdPs don't provide a username (looking at you Google), so if we don't have the claim,
                # we'll create the user with whatever the USER_CLAIM is (default email)
                username = claims.get(
                    "preferred_username", claims.get("username", claims.get(settings.OIDC_USER_CLAIM))
                )
                user = repos.users.create(
                    {
                        "username": username,
                        "password": "OIDC",
                        "full_name": claims.get(settings.OIDC_NAME_CLAIM),
                        "email": claims.get("email"),
                        "admin": is_admin,
                        "auth_method": AuthMethod.OIDC,
                    }
                )
                self.session.commit()
                self._update_profile_image_from_claim(user.id, claims)

            except Exception as e:
                self._logger.error("[OIDC] Exception while creating user: %s", e)
                return None

            return self.get_access_token(user, settings.OIDC_REMEMBER_ME)  # type: ignore

        # A matched account is adopted here (including local/LDAP accounts). This is
        # safe because the email that produced the match was verified by the IdP
        # above, unless the admin has explicitly disabled that requirement.
        if settings.OIDC_ADMIN_GROUP and user.admin != is_admin:
            self._logger.debug("[OIDC] %s user as admin", "Setting" if is_admin else "Removing")
            user.admin = is_admin
            repos.users.update(user.id, user)
        self._update_profile_image_from_claim(user.id, claims)
        return self.get_access_token(user, settings.OIDC_REMEMBER_ME)

    @property
    def required_claims(self):
        settings = get_app_settings()

        claims = {settings.OIDC_NAME_CLAIM, "email", settings.OIDC_USER_CLAIM}
        if settings.OIDC_REQUIRES_GROUP_CLAIM and not self.use_default_groups:
            claims.add(settings.OIDC_GROUPS_CLAIM)
        return claims

    def _is_safe_picture_url(self, url: str) -> bool:
        """
        Vets the picture claim before we make a request to it.

        The claim is not necessarily set by the provider -- IdPs that let users edit their own
        profile would otherwise hand any user a request-forgery primitive -- so the URL must use
        HTTPS and resolve to a public address. The exception is the provider's own host, which
        Mealie already contacts on every login and which self-hosted setups routinely run on a
        private network, often over plain HTTP.
        """
        settings = get_app_settings()
        parsed = urlparse(url)
        host = parsed.hostname
        if not host:
            return False

        if settings.OIDC_CONFIGURATION_URL and host == urlparse(settings.OIDC_CONFIGURATION_URL).hostname:
            return parsed.scheme in ("http", "https")

        if parsed.scheme != "https":
            self._logger.warning("[OIDC] refusing to fetch profile image over a non-HTTPS URL")
            return False

        try:
            addresses = {info[4][0] for info in socket.getaddrinfo(host, None)}
        except (socket.gaierror, UnicodeError):
            # `UnicodeError`, not `gaierror`, is what an unencodable hostname raises.
            return False

        # `is_global` is false for private, loopback and link-local ranges, so a single check
        # covers RFC1918, 127/8, and the 169.254.169.254 cloud metadata endpoint.
        if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
            self._logger.warning("[OIDC] refusing to fetch profile image from a non-public address")
            return False

        return True

    def _fetch_picture(self, url: str) -> requests.Response:
        """
        Fetches `url`, following redirects only to hosts that pass the same vetting.

        `requests` follows redirects itself by default, which would let a vetted URL hand us off
        to a host nobody checked -- the validation has to be re-applied per hop, not once up
        front. So we follow them ourselves and run every target through `_is_safe_picture_url`
        before requesting it.
        """
        for _ in range(MAX_PICTURE_REDIRECTS + 1):
            response = requests.get(url, timeout=15, stream=True, allow_redirects=False)
            if not response.is_redirect:
                response.raise_for_status()
                return response

            location = response.headers.get("location", "")
            # The body is streamed, so an intermediate response holds its connection open.
            response.close()

            if not location:
                raise ValueError("redirect without a Location header")

            # A Location may be relative (RFC 9110), so resolve it against the URL we just asked.
            url = urljoin(url, location)
            if not self._is_safe_picture_url(url):
                raise ValueError("refusing to follow redirect to an unvetted host")

        raise ValueError(f"profile image exceeded {MAX_PICTURE_REDIRECTS} redirects")

    @staticmethod
    def _read_capped(response: requests.Response) -> bytes:
        """Reads the body, refusing anything over `MAX_PICTURE_BYTES`."""
        declared_length = response.headers.get("content-length")
        if declared_length and declared_length.isdigit() and int(declared_length) > MAX_PICTURE_BYTES:
            raise ValueError(f"declared content-length {declared_length} exceeds {MAX_PICTURE_BYTES} bytes")

        content = bytearray()
        for chunk in response.iter_content(chunk_size=8192):
            content.extend(chunk)
            # Servers that omit or understate Content-Length are caught by the running total.
            if len(content) > MAX_PICTURE_BYTES:
                raise ValueError(f"profile image exceeds {MAX_PICTURE_BYTES} bytes")
        return bytes(content)

    def _update_profile_image_from_claim(self, user_id: UUID4, claims: UserInfo) -> None:
        picture = claims.get("picture")
        if not picture or not isinstance(picture, str):
            return

        # The claim is attacker-controlled on IdPs that let users edit their own profile, and a
        # value that trips up parsing or resolution must skip the avatar, never fail the login.
        try:
            if not self._is_safe_picture_url(picture):
                return

            repos = get_repositories(self.session, group_id=None, household_id=None)
            user = repos.users.get_one(user_id)
            if user is None:
                return

            # Skip the download entirely when the claim still points at the image we already stored.
            picture_hash = hashlib.sha256(picture.encode()).hexdigest()
            if user.external_avatar_hash == picture_hash:
                return

            response = self._fetch_picture(picture)
            content = self._read_capped(response)

            with get_temporary_path() as temp_path:
                temp_img = Path(temp_path).joinpath(str(uuid4()))
                temp_img.write_bytes(content)

                image = img.PillowMinifier.to_webp(temp_img)
                dest = PrivateUser.get_directory(user_id) / "profile.webp"
                shutil.move(image, dest)

            repos.users.patch(user_id, {"cache_key": cache.new_key(), "external_avatar_hash": picture_hash})
        except Exception as e:
            self._logger.debug("[OIDC] Could not update profile image from picture claim: %s", e)
