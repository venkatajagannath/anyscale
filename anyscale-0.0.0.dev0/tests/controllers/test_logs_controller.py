import datetime
from datetime import timedelta
import os
import random
import shutil
import string
import tempfile
from typing import Any
from unittest.mock import call, patch

from anyscale.client.openapi_client.models import (
    LogDownloadConfig,
    LogDownloadRequest,
    LogDownloadResult,
    LogdownloadresultResponse,
    LogFileChunk,
    LogFilter,
)
from anyscale.controllers.logs_controller import LogsController


MOCK_COMBINED_LOGS = """
{"filename": "a", "message": "a"}
{"filename": "b", "message": "b"}
{"filename": "c", "message": "c"}
{"filename": "d", "message": "d"}
{"filename": "b", "message": "b"}
{"filename": "c", "message": "c"}
{"filename": "d", "message": "d"}
{"filename": "c", "message": "c"}
{"filename": "d", "message": "d"}
{"filename": "d", "message": "d"}
""".strip()

EXPECTED_UNCOMBINED_CONTENTS = {
    "a": "\n".join("a"),
    "b": "\n".join("bb"),
    "c": "\n".join("ccc"),
    "d": "\n".join("dddd"),
}


class AsyncBytesIterator:
    def __init__(self, data: bytes, n: int) -> None:
        self.data = data
        self.n = n
        self.read = 0

    def __aiter__(self):  # type: ignore
        return self

    async def __anext__(self) -> bytes:
        if not self.data[self.read :]:
            raise StopAsyncIteration
        _bytes = self.data[self.read : self.read + self.n]
        self.read += self.n
        return _bytes


class AsyncStreamReader:
    def __init__(self, _bytes: bytes) -> None:
        self._bytes = _bytes

    def iter_chunked(self, n: int) -> AsyncBytesIterator:
        return AsyncBytesIterator(self._bytes, n)


class AsyncMockResponse:
    def __init__(self, resp: str, status: int) -> None:
        self._bytes = bytes(resp, "utf-8")
        self.status = status
        self.content = AsyncStreamReader(self._bytes)

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        pass

    async def __aenter__(self):  # type: ignore
        return self

    async def text(self):  # type: ignore
        return self._bytes.decode("utf-8")


def test_download_log_files(mock_auth_api_client) -> None:  # type: ignore
    """Test that the download_log_files is able to download files correctly.
    Also verify handling of error response while downloading files.
    Also test handling of paginated response.
    """
    logs_controller = LogsController()
    data = ["".join(random.choices(string.ascii_lowercase, k=5)) for x in range(2)]
    data.append("error response")
    data.append(MOCK_COMBINED_LOGS)
    dirpath = tempfile.mkdtemp()
    try:
        logs_controller.api_client.get_log_files_api_v2_logs_get_log_files_post.side_effect = [
            LogdownloadresultResponse(
                result=LogDownloadResult(
                    log_chunks=[
                        LogFileChunk(
                            chunk_name="logs/test1.txt/chunk_one.log",
                            chunk_url="http://test.com",
                            size=len(data[0]),
                            cluster_id="cluster-id",
                            file_name="test1.txt",
                            node_type="head-node",
                            node_ip="ip",
                            instance_id="id",
                            session_id="session-id",
                        )
                    ],
                    next_page_token="foo",
                )
            ),
            LogdownloadresultResponse(
                result=LogDownloadResult(
                    log_chunks=[
                        LogFileChunk(
                            chunk_name="logs/events/test2.txt/chunk_one.log",
                            chunk_url="http://test.com",
                            size=len(data[1]),
                            cluster_id="cluster-id",
                            file_name="events/test2.txt",
                            node_type="head-node",
                            node_ip="ip",
                            instance_id="id",
                            session_id="session-id",
                        ),
                        LogFileChunk(
                            chunk_name="logs/test3.txt/chunk_one.log",
                            chunk_url="http://test.com",
                            size=len(data[2]),
                            cluster_id="cluster-id",
                            file_name="test3.txt",
                            node_type="head-node",
                            node_ip="ip",
                            instance_id="id",
                            session_id="session-id",
                        ),
                        LogFileChunk(
                            chunk_name="logs/combined-worker.log/chunk_one.log",
                            chunk_url="http://test.com",
                            size=len(data[3]),
                            cluster_id="cluster-id",
                            file_name="combined-worker.log",
                            node_type="head-node",
                            node_ip="ip",
                            instance_id="id",
                            session_id="session-id",
                        ),
                    ],
                    next_page_token=None,
                )
            ),
        ]

        with patch(
            "aiohttp.ClientSession.get",
            side_effect=[
                AsyncMockResponse(data[0], 200),
                AsyncMockResponse(data[1], 200),
                AsyncMockResponse(data[2], 500),
                AsyncMockResponse(data[3], 200),
            ],
        ):
            logs_controller.download_logs(
                filter=LogFilter(cluster_id="abc"),
                download_dir=dirpath,
                ttl_seconds=600,
                read_timeout=timedelta(5),
                parallelism=5,
                page_size=1000,
                timeout=timedelta(5),
                unpack=True,
            )
        with open(f"{dirpath}/logs/cluster-id/session-id/head-ip-id/test1.txt") as f:
            assert f.read().strip() == data[0].strip()
        with open(
            f"{dirpath}/logs/cluster-id/session-id/head-ip-id/events/test2.txt"
        ) as f:
            assert f.read().strip() == data[1].strip()
        for k, v in EXPECTED_UNCOMBINED_CONTENTS.items():
            with open(f"{dirpath}/logs/cluster-id/session-id/head-ip-id/{k}") as f:
                assert f.read().strip() == v

        assert not os.path.exists(
            f"{dirpath}/logs/cluster-id/session-id/head-ip-id/test3.txt"
        )
        assert (
            logs_controller.api_client.get_log_files_api_v2_logs_get_log_files_post.call_args_list
            == [
                call(
                    log_download_request=LogDownloadRequest(
                        filter=LogFilter(cluster_id="abc"),
                        config=LogDownloadConfig(
                            page_size=1000, ttl_seconds=600, use_bearer_token=True
                        ),
                    ),
                    _request_timeout=datetime.timedelta(days=5),
                ),
                call(
                    log_download_request=LogDownloadRequest(
                        filter=LogFilter(cluster_id="abc"),
                        config=LogDownloadConfig(
                            next_page_token="foo",
                            page_size=1000,
                            ttl_seconds=600,
                            use_bearer_token=True,
                        ),
                    ),
                    _request_timeout=datetime.timedelta(days=5),
                ),
            ]
        )

    finally:
        shutil.rmtree(dirpath)
