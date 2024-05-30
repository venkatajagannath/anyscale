from dataclasses import dataclass
import os
from typing import List, Optional

from anyscale.cli_logger import BlockLogger
from anyscale.sdk.anyscale_client.configuration import Configuration


OPENAPI_NO_VALIDATION = Configuration()
OPENAPI_NO_VALIDATION.client_side_validation = False

TEST_COMPUTE_CONFIG_DICT = {
    "cloud": "fake-cloud",
    "head_node": {"instance_type": "fake-instance-type",},
    "worker_nodes": [],
}

TEST_CONTAINERFILE = os.path.join(
    os.path.dirname(__file__), "test_files/containerfiles", "Containerfile",
)


@dataclass
class RequirementsFile:
    name: str
    expected_pip_list: Optional[List[str]]

    def get_path(self) -> str:
        return os.path.join(
            os.path.dirname(__file__), "test_files/requirements_files", self.name,
        )


SINGLE_LINE_REQUIREMENTS = RequirementsFile("single_line.txt", ["pip-install-test"])
MULTI_LINE_REQUIREMENTS = RequirementsFile(
    "multi_line.txt", ["pip-install-test", "torch==1.10.1"]
)

TEST_REQUIREMENTS_FILES = [
    SINGLE_LINE_REQUIREMENTS,
    MULTI_LINE_REQUIREMENTS,
    RequirementsFile("does_not_exist.txt", None),
    RequirementsFile("empty.txt", []),
    RequirementsFile(
        "multi_line_with_whitespace.txt",
        ["pip-install-test", "torch==1.10.1", "something-else"],
    ),
    RequirementsFile("comments.txt", ["pip-install-test", "torch==1.10.1"]),
]


class TestLogger:
    def __init__(self):
        self._delegate = BlockLogger()
        self._info_messages: List[str] = []
        self._warning_messages: List[str] = []
        self._error_messages: List[str] = []

    @property
    def info_messages(self) -> List[str]:
        return self._info_messages

    def info(self, msg: str, end: str = "\n"):
        self._info_messages.append(msg)
        self._delegate.info(msg)

    @property
    def warning_messages(self) -> List[str]:
        return self._warning_messages

    def warning(self, msg: str):
        self._warning_messages.append(msg)
        self._delegate.warning(msg)

    @property
    def error_messages(self) -> List[str]:
        return self._error_messages

    def error(self, msg: str):
        self._error_messages.append(msg)
        self._delegate.error(msg)
