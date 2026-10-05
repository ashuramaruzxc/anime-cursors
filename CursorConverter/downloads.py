"""Download checksum-pinned archives using only the Python standard library"""

import argparse
import hashlib
import html
import http.client
import json
import os
import re
import shutil
import ssl
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from collections.abc import Iterator
from contextlib import contextmanager
from email.utils import parsedate_to_datetime
from pathlib import Path
from threading import Condition, Lock
from typing import NotRequired, TypedDict, cast

REQUEST_INTERVAL = 2.0
REQUEST_TIMEOUT = 60
USER_AGENT = "anime-cursors/1.0"
MAX_DOWNLOAD_ATTEMPTS = 5
RETRY_BACKOFF_BASE = 2
COOLDOWN_STATUS_CODES = frozenset({429, 503})
RETRYABLE_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})
CHECKSUM_ALGORITHM = "sha256"
PAGE_ENCODING = "utf-8"
AXFC_ARCHIVE_KIND = "axfc"
AXFC_FORM_PATH = "/u/dl2.pl"
AXFC_FORM_FIELDS = frozenset({"sid", "dqn"})
AXFC_FORM_FIELD_PATTERN = re.compile(r'name="(sid|dqn)" value="([^"]*)"')
AXFC_DOWNLOAD_LINK_PATTERN = re.compile(r'href="([^"]*link\.pl[^\"]*)"')
AXFC_FILE_LINK_PATTERN = re.compile(r'href="(https?://[^\"]+\.axfc\.net/d/[^\"]*)"')


class DownloadQueue:
    """Admit one archive at a time in arrival order within this process"""

    def __init__(self) -> None:
        self.pending: deque[object] = deque()
        self.condition = Condition()

    @contextmanager
    def slot(self) -> Iterator[None]:
        ticket = object()
        with self.condition:
            self.pending.append(ticket)
        try:
            with self.condition:
                self.condition.wait_for(lambda: self.pending[0] is ticket)
            yield
        finally:
            with self.condition:
                self.pending.remove(ticket)
                self.condition.notify_all()


class RequestPacer(urllib.request.BaseHandler):
    """Space every HTTP request, including redirects, without accumulating bursts"""

    def __init__(self) -> None:
        self.lock = Lock()
        # The initial pause also separates downloads in sequential Nix builder processes
        self.next_request = time.monotonic() + REQUEST_INTERVAL

    def http_request(self, request: urllib.request.Request) -> urllib.request.Request:
        with self.lock:
            while True:
                delay = self.next_request - time.monotonic()
                if delay <= 0:
                    break
                time.sleep(delay)
            self.next_request = time.monotonic() + REQUEST_INTERVAL
        return request

    https_request = http_request

    def defer(self, delay: float) -> None:
        with self.lock:
            deferred_until = time.monotonic() + delay
            self.next_request = max(self.next_request, deferred_until)


DOWNLOAD_QUEUE = DownloadQueue()
REQUEST_PACER = RequestPacer()


class Archive(TypedDict):
    url: str
    sha256: str
    page: str
    kind: NotRequired[str]
    keyword: NotRequired[str]


class DownloadLinkError(ValueError):
    """The archive host did not provide a usable download link"""


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        checksum = hashlib.file_digest(stream, CHECKSUM_ALGORITHM)
        return checksum.hexdigest()


def open_url(url: str, data: bytes | None = None):
    request = urllib.request.Request(url, data, headers={"User-Agent": USER_AGENT})
    # Load the CA bundle explicitly because OpenSSL can ignore environment paths in Nix sandboxes
    ca_file = os.environ.get("SSL_CERT_FILE")
    context = ssl.create_default_context(cafile=ca_file)
    https_handler = urllib.request.HTTPSHandler(context=context)
    opener = urllib.request.build_opener(REQUEST_PACER, https_handler)
    try:
        return opener.open(request, timeout=REQUEST_TIMEOUT)
    except urllib.error.HTTPError as error:
        if error.code in COOLDOWN_STATUS_CODES:
            delay = retry_after(error)
            REQUEST_PACER.defer(delay)
        raise


def retry_after(error: urllib.error.HTTPError) -> float:
    """Respect server cooldowns expressed as seconds or an HTTP date"""
    value = error.headers.get("Retry-After", "")
    if value.isascii() and value.isdigit():
        return float(value)
    try:
        retry_date = parsedate_to_datetime(value)
        delay = retry_date.timestamp() - time.time()
        return max(0.0, delay)
    except ValueError, TypeError, OverflowError:
        return REQUEST_INTERVAL


def axfc_download_url(archive: Archive) -> str:
    # Axfc issues a short-lived file URL after submitting the public download form
    with open_url(archive["url"]) as response:
        page = response.read().decode(PAGE_ENCODING)
        url = response.url
    fields = dict(AXFC_FORM_FIELD_PATTERN.findall(page))
    if fields.keys() != AXFC_FORM_FIELDS:
        raise DownloadLinkError(f"Axfc download form unavailable: {archive['url']}")
    fields["keyword"] = archive.get("keyword", "")
    form_data = urllib.parse.urlencode(fields)
    body = form_data.encode()
    form_url = urllib.parse.urljoin(url, AXFC_FORM_PATH)
    with open_url(form_url, body) as response:
        page = response.read().decode(PAGE_ENCODING)
        url = response.url
    link = AXFC_DOWNLOAD_LINK_PATTERN.search(page)
    if link is None:
        raise DownloadLinkError(f"Axfc did not provide a download link: {archive['url']}")
    download_link = html.unescape(link[1])
    download_url = urllib.parse.urljoin(url, download_link)
    with open_url(download_url) as response:
        page = response.read().decode(PAGE_ENCODING)
    link = AXFC_FILE_LINK_PATTERN.search(page)
    if link is None:
        raise DownloadLinkError(f"Axfc file link unavailable: {archive['url']}")
    return html.unescape(link[1])


def download_archive(archive: Archive, destination: Path) -> None:
    with DOWNLOAD_QUEUE.slot():
        # Check inside the queue so concurrent callers do not fetch the same cached archive twice
        if destination.is_file() and digest(destination) == archive["sha256"]:
            return
        _download_archive(archive, destination)


def _download_archive(archive: Archive, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as directory:
        temporary = Path(directory) / destination.name
        for attempt in range(MAX_DOWNLOAD_ATTEMPTS):
            try:
                # Restart the form flow because Axfc links expire and error pages can be temporary
                if archive.get("kind") == AXFC_ARCHIVE_KIND:
                    url = axfc_download_url(archive)
                else:
                    url = archive["url"]
                with temporary.open("wb") as stream, open_url(url) as response:
                    shutil.copyfileobj(response, stream)
                break
            except (
                DownloadLinkError,
                urllib.error.URLError,
                TimeoutError,
                ConnectionError,
                http.client.IncompleteRead,
            ) as error:
                if isinstance(error, urllib.error.HTTPError):
                    error.close()
                    if error.code not in RETRYABLE_STATUS_CODES:
                        raise
                if attempt == MAX_DOWNLOAD_ATTEMPTS - 1:
                    raise
                delay = RETRY_BACKOFF_BASE**attempt
                print(f"Download failed ({error}); retrying in {delay}s", file=sys.stderr, flush=True)
                time.sleep(delay)
        if digest(temporary) != archive["sha256"]:
            raise ValueError(f"Archive checksum mismatch: {archive['url']}")
        temporary.replace(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="JSON archive description")
    parser.add_argument("output", type=Path, help="Destination for the verified archive")
    args = parser.parse_args()
    archive_data = args.archive.read_text()
    archive = cast(Archive, json.loads(archive_data))
    download_archive(archive, args.output)


if __name__ == "__main__":
    main()
