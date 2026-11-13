from collections.abc import Iterator

import pytest
from fastapi import FastAPI, File, UploadFile
from fastapi.testclient import TestClient

from mealie.middleware.body_size_limit import BodySizeLimitMiddleware

LIMIT = 1024


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.add_middleware(BodySizeLimitMiddleware, max_body_size=LIMIT)

    @app.post("/upload")
    def upload(archive: UploadFile = File(...)) -> int:
        return len(archive.file.read())

    return TestClient(app)


def test_allows_body_under_limit(client: TestClient):
    response = client.post("/upload", files={"archive": b"0" * 100})

    assert response.status_code == 200
    assert response.json() == 100


def test_rejects_declared_length_over_limit(client: TestClient):
    response = client.post("/upload", files={"archive": b"0" * (LIMIT * 2)})

    assert response.status_code == 413


def test_rejects_chunked_body_over_limit(client: TestClient):
    boundary = "limit-test"

    def chunks() -> Iterator[bytes]:
        yield (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="archive"; filename="a.zip"\r\n'
            "Content-Type: application/zip\r\n\r\n"
        ).encode()
        for _ in range(4):
            yield b"0" * LIMIT
        yield f"\r\n--{boundary}--\r\n".encode()

    response = client.post(
        "/upload", content=chunks(), headers={"content-type": f"multipart/form-data; boundary={boundary}"}
    )

    assert "content-length" not in {k.lower() for k in response.request.headers}
    assert response.status_code == 413
