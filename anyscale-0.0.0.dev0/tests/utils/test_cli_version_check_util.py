from typing import Optional

import pytest

from anyscale.utils.cli_version_check_util import _is_upgrade_needed


@pytest.mark.parametrize(
    ("local_anyscale_version", "latest_version", "expected"),
    [
        ["0.0.0-dev", None, False],
        ["0.0.0-dev", "0.5.122", False],
        ["0.5.92", "0.5.122", True],
        ["0.5.92", "1.0.0", True],
        ["0.5.123", "0.5.122", False],
        ["0.5.122", "0.5.122", False],
    ],
)
def test_should_warn_version(
    local_anyscale_version: str, latest_version: Optional[str], expected: bool
):
    result = _is_upgrade_needed(local_anyscale_version, latest_version)
    assert result == expected
