from unittest.mock import patch

from asynctest import CoroutineMock
import pytest

from anyscale.api_utils import logs_util
from anyscale.api_utils.logs_util import (
    _download_log_from_s3_url,
    _remove_ansi_escape_sequences,
)


# Indirectly tests gather_in_batches()
async def test_download_logs_concurrently():
    # Test all downloads succeed
    with patch.object(
        logs_util,
        _download_log_from_s3_url.__name__,
        CoroutineMock(side_effect=["logs_from_chunk_1\n", "logs_from_chunk_2"]),
    ) as mock_download_log_from_s3_url:
        result = await logs_util._download_logs_concurrently(
            ["http://presigned.url.1", "http://presigned.url.2"], 1
        )
    assert result == "logs_from_chunk_1\nlogs_from_chunk_2"
    assert mock_download_log_from_s3_url.call_count == 2

    # Test one download fail raise exception
    exception_msg = "Log chunk download failed"
    with patch.object(
        logs_util,
        _download_log_from_s3_url.__name__,
        CoroutineMock(side_effect=Exception(exception_msg)),
    ) as mock_download_log_from_s3_url, pytest.raises(Exception, match=exception_msg):
        result = await logs_util._download_logs_concurrently(
            ["http://presigned.url.1", "http://presigned.url.2"], 1
        )


def test_remove_ansi_escape_sequences():
    string_with_ansi_escape_sequences = "\x1b[1m\x1b[31mHello World\x1B[0m\x1B[0m"
    assert (
        _remove_ansi_escape_sequences(string_with_ansi_escape_sequences)
        == "Hello World"
    )
