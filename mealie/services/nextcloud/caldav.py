"""Nextcloud Tasks integration via CalDAV (VTODO).

Manages CalDAV VTODO operations against a Nextcloud instance for syncing
Mealie shopping lists with Nextcloud Tasks.

Uses synchronous httpx.Client to avoid async/thread issues when called
from SQLAlchemy-bound sync code.
"""

import logging
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import unquote, urlparse, urlunparse
from uuid import uuid4

import httpx

logger = logging.getLogger(__name__)

_CALDAV_REPORT = """<?xml version="1.0" encoding="UTF-8"?>
<c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">
  <d:prop><c:calendar-data/></d:prop>
  <c:filter>
    <c:comp-filter name="VCALENDAR">
      <c:comp-filter name="VTODO"/>
    </c:comp-filter>
  </c:filter>
</c:calendar-query>"""


@dataclass
class VTodoItem:
    uid: str
    summary: str
    status: str = "NEEDS-ACTION"
    parent_uid: str = ""
    completed: str | None = None
    last_modified: str | None = None
    description: str | None = None


@dataclass
class CalendarInfo:
    slug: str
    display_name: str = ""


def _is_docker() -> bool:
    return os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv")


def _fix_docker_localhost(url: str) -> str:
    if not url:
        return url
    parsed = urlparse(url)
    if parsed.hostname in ("localhost", "127.0.0.1") and _is_docker():
        gateway = "172.17.0.1"
        new_netloc = f"{gateway}:{parsed.port}" if parsed.port else gateway
        return urlunparse(parsed._replace(netloc=new_netloc))
    return url


def _ical_field(block: str, name: str) -> str | None:
    m = re.search(rf"^{name}:(.*)", block, re.MULTILINE)
    return m.group(1).strip() if m else None


def _parse_vtodos(xml_text: str) -> list[VTodoItem]:
    tasks = []
    for vcal_match in re.finditer(r"BEGIN:VTODO(.*?)END:VTODO", xml_text, re.DOTALL):
        block = vcal_match.group(1)
        uid = _ical_field(block, "UID")
        if not uid:
            continue

        parent_match = re.search(r"RELATED-TO;RELTYPE=PARENT:(.*)", block)
        parent_uid = parent_match.group(1).strip() if parent_match else ""

        tasks.append(
            VTodoItem(
                uid=uid,
                summary=_ical_field(block, "SUMMARY") or "",
                status=_ical_field(block, "STATUS") or "NEEDS-ACTION",
                parent_uid=parent_uid,
                completed=_ical_field(block, "COMPLETED"),
                last_modified=_ical_field(block, "LAST-MODIFIED"),
                description=_ical_field(block, "DESCRIPTION"),
            )
        )
    return tasks


def _build_vtodo(uid: str, summary: str, parent_uid: str = "", status: str = "NEEDS-ACTION") -> str:
    now = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    related_line = f"RELATED-TO;RELTYPE=PARENT:{parent_uid}\r\n" if parent_uid else ""
    completed_line = f"COMPLETED:{now}\r\n" if status == "COMPLETED" else ""
    return (
        f"BEGIN:VCALENDAR\r\n"
        f"VERSION:2.0\r\n"
        f"PRODID:-//Mealie//CalDAV//EN\r\n"
        f"BEGIN:VTODO\r\n"
        f"UID:{uid}\r\n"
        f"DTSTAMP:{now}\r\n"
        f"CREATED:{now}\r\n"
        f"LAST-MODIFIED:{now}\r\n"
        f"SUMMARY:{summary}\r\n"
        f"STATUS:{status}\r\n"
        f"{related_line}"
        f"{completed_line}"
        f"END:VTODO\r\n"
        f"END:VCALENDAR\r\n"
    )


class NextcloudTasksService:
    """Manages CalDAV VTODO operations against a Nextcloud instance.

    All methods are synchronous, using httpx.Client.
    """

    def __init__(self, url: str, username: str, password: str, task_list: str, verify_ssl: bool = True) -> None:
        self.url = _fix_docker_localhost(url.rstrip("/")) if url else ""
        self.username = username
        self.password = password
        self.task_list = task_list
        self.verify_ssl = verify_ssl
        self._resolved_slug: str | None = None

    def _client(self) -> httpx.Client:
        return httpx.Client(timeout=15, verify=self.verify_ssl)

    def _resolve_calendar_slug(self, client: httpx.Client) -> str | None:
        if self._resolved_slug:
            return self._resolved_slug

        calendars_url = f"{self.url}/remote.php/dav/calendars/{self.username}/"
        try:
            resp = client.request(
                "PROPFIND",
                calendars_url,
                auth=(self.username, self.password),
                headers={"Depth": "1"},
            )
            if resp.status_code not in (200, 207):
                logger.error("CalDAV PROPFIND failed: HTTP %d", resp.status_code)
                return None

            hrefs = re.findall(r"<(?:d|D):href>([^<]+)</(?:d|D):href>", resp.text)
            slugs = []
            for href in hrefs:
                slug = href.rstrip("/").rsplit("/", 1)[-1]
                if slug and slug != self.username:
                    slugs.append(slug)

            logger.debug("Available calendar slugs: %s", slugs)

            for slug in slugs:
                if slug == self.task_list:
                    self._resolved_slug = slug
                    return slug

            for slug in slugs:
                if unquote(slug) == self.task_list:
                    self._resolved_slug = slug
                    return slug

            for slug in slugs:
                if slug.lower() == self.task_list.lower() or unquote(slug).lower() == self.task_list.lower():
                    self._resolved_slug = slug
                    return slug

            ascii_target = "".join(c for c in self.task_list if (c.isascii() and c.isalnum()) or c == "-")
            for slug in slugs:
                if slug and slug == ascii_target:
                    self._resolved_slug = slug
                    return slug

            for slug in slugs:
                try:
                    cal_url = f"{self.url}/remote.php/dav/calendars/{self.username}/{slug}/"
                    r = client.request(
                        "PROPFIND",
                        cal_url,
                        auth=(self.username, self.password),
                        headers={"Depth": "0"},
                    )
                    if r.status_code in (200, 207):
                        dn = re.search(r"<(?:d|D):displayname>([^<]*)</(?:d|D):displayname>", r.text)
                        if dn and dn.group(1) == self.task_list:
                            logger.info("Matched task list '%s' to slug '%s' via display name", self.task_list, slug)
                            self._resolved_slug = slug
                            return slug
                except Exception:
                    continue

            logger.error("Task list '%s' not found. Available slugs: %s", self.task_list, slugs)
        except Exception as e:
            logger.error("PROPFIND for calendar slug failed: %s", e)
        return None

    def _get_calendar_url(self, client: httpx.Client) -> str | None:
        slug = self._resolve_calendar_slug(client)
        if not slug:
            return None
        return f"{self.url}/remote.php/dav/calendars/{self.username}/{slug}/"

    def test_connection(self) -> dict:
        """Test connection and return available task lists."""
        calendars_url = f"{self.url}/remote.php/dav/calendars/{self.username}/"
        try:
            with self._client() as client:
                resp = client.request(
                    "PROPFIND",
                    calendars_url,
                    auth=(self.username, self.password),
                    headers={"Depth": "1"},
                )
                if resp.status_code not in (200, 207):
                    return {"status": "error", "message": f"HTTP {resp.status_code}"}

                calendars: list[CalendarInfo] = []
                hrefs = re.findall(r"<(?:d|D):href>([^<]+)</(?:d|D):href>", resp.text)
                for href in hrefs:
                    slug = href.rstrip("/").rsplit("/", 1)[-1]
                    if slug and slug != self.username:
                        calendars.append(CalendarInfo(slug=slug))

                for cal in calendars:
                    try:
                        cal_url = f"{self.url}/remote.php/dav/calendars/{self.username}/{cal.slug}/"
                        r = client.request(
                            "PROPFIND",
                            cal_url,
                            auth=(self.username, self.password),
                            headers={"Depth": "0"},
                        )
                        if r.status_code in (200, 207):
                            dn = re.search(r"<(?:d|D):displayname>([^<]*)</(?:d|D):displayname>", r.text)
                            if dn:
                                cal.display_name = dn.group(1)
                    except Exception:
                        continue

                return {
                    "status": "ok",
                    "calendars": [{"slug": c.slug, "display_name": c.display_name} for c in calendars],
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_todos(self) -> list[VTodoItem]:
        """Fetch all VTODOs from the configured task list."""
        with self._client() as client:
            cal_url = self._get_calendar_url(client)
            if not cal_url:
                return []

            resp = client.request(
                "REPORT",
                cal_url,
                auth=(self.username, self.password),
                headers={"Depth": "1", "Content-Type": "application/xml"},
                content=_CALDAV_REPORT,
            )
            if resp.status_code not in (200, 207):
                logger.error("CalDAV REPORT failed: HTTP %d", resp.status_code)
                return []

            return _parse_vtodos(resp.text)

    def create_todo(
        self, summary: str, parent_uid: str = "", uid: str | None = None, status: str = "NEEDS-ACTION"
    ) -> str | None:
        """Create a VTODO. Returns the UID on success."""
        uid = uid or str(uuid4())
        vtodo = _build_vtodo(uid, summary, parent_uid=parent_uid, status=status)

        with self._client() as client:
            cal_url = self._get_calendar_url(client)
            if not cal_url:
                return None

            resp = client.put(
                f"{cal_url}{uid}.ics",
                content=vtodo,
                headers={"Content-Type": "text/calendar; charset=utf-8"},
                auth=(self.username, self.password),
            )
            if resp.status_code in (200, 201, 204):
                logger.info("Created VTODO: %s (uid=%s)", summary, uid)
                return uid
            logger.error("CalDAV PUT failed: HTTP %d", resp.status_code)
            return None

    def update_todo_summary(self, uid: str, summary: str) -> bool:
        """Update the summary of a VTODO."""
        with self._client() as client:
            cal_url = self._get_calendar_url(client)
            if not cal_url:
                return False

            item_url = f"{cal_url}{uid}.ics"
            resp = client.get(item_url, auth=(self.username, self.password))
            if resp.status_code != 200:
                return False

            vcal = re.sub(r"SUMMARY:[^\r\n]+", f"SUMMARY:{summary}", resp.text)
            vcal = re.sub(
                r"LAST-MODIFIED:[^\r\n]+",
                f"LAST-MODIFIED:{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}",
                vcal,
            )

            resp = client.put(
                item_url,
                content=vcal,
                headers={"Content-Type": "text/calendar; charset=utf-8"},
                auth=(self.username, self.password),
            )
            return resp.status_code in (200, 201, 204)

    def complete_todo(self, uid: str) -> bool:
        """Mark a VTODO as COMPLETED."""
        with self._client() as client:
            cal_url = self._get_calendar_url(client)
            if not cal_url:
                return False

            item_url = f"{cal_url}{uid}.ics"
            resp = client.get(item_url, auth=(self.username, self.password))
            if resp.status_code != 200:
                return False

            vcal = resp.text
            now = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
            vcal = re.sub(r"STATUS:[^\r\n]+", "STATUS:COMPLETED", vcal)
            vcal = re.sub(
                r"LAST-MODIFIED:[^\r\n]+",
                f"LAST-MODIFIED:{now}",
                vcal,
            )
            if "COMPLETED:" not in vcal:
                vcal = vcal.replace("END:VTODO", f"COMPLETED:{now}\r\nEND:VTODO")

            resp = client.put(
                item_url,
                content=vcal,
                headers={"Content-Type": "text/calendar; charset=utf-8"},
                auth=(self.username, self.password),
            )
            return resp.status_code in (200, 201, 204)

    def uncomplete_todo(self, uid: str) -> bool:
        """Remove COMPLETED status and set to NEEDS-ACTION."""
        with self._client() as client:
            cal_url = self._get_calendar_url(client)
            if not cal_url:
                return False

            item_url = f"{cal_url}{uid}.ics"
            resp = client.get(item_url, auth=(self.username, self.password))
            if resp.status_code != 200:
                return False

            vcal = resp.text
            vcal = re.sub(r"COMPLETED:[^\r\n]+\r?\n", "", vcal)
            vcal = re.sub(r"STATUS:[^\r\n]+", "STATUS:NEEDS-ACTION", vcal)
            vcal = re.sub(
                r"LAST-MODIFIED:[^\r\n]+",
                f"LAST-MODIFIED:{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}",
                vcal,
            )

            resp = client.put(
                item_url,
                content=vcal,
                headers={"Content-Type": "text/calendar; charset=utf-8"},
                auth=(self.username, self.password),
            )
            return resp.status_code in (200, 201, 204)

    def delete_todo(self, uid: str) -> bool:
        """Delete a VTODO by UID."""
        with self._client() as client:
            cal_url = self._get_calendar_url(client)
            if not cal_url:
                return False

            resp = client.delete(f"{cal_url}{uid}.ics", auth=(self.username, self.password))
            if resp.status_code in (200, 204):
                logger.info("Deleted VTODO: uid=%s", uid)
                return True
            logger.error("CalDAV DELETE failed: HTTP %d", resp.status_code)
            return False
