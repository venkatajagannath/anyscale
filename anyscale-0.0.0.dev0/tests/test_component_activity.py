import json
import os
import shutil
import tempfile
from typing import Optional
from unittest.mock import MagicMock, patch

from anyscale import component_activity_util


class StatusFile:
    is_active: str
    reason: str
    timestamp: float
    last_activity_timestamp: float


class TestComponentActivityEnv:
    def __init__(self, idle_termination_dir: Optional[str] = None):
        if idle_termination_dir:
            self.idle_termination_dir = idle_termination_dir
            component_activity_util.IDLE_TERMINATION_DIR = idle_termination_dir

    def write_status_file(self, file_name: str, content):
        with open(f"{self.idle_termination_dir}/{file_name}.json", "w") as f:
            f.write(json.dumps(content))

    def __del__(self):
        if self.idle_termination_dir and os.path.exists(self.idle_termination_dir):
            shutil.rmtree(self.idle_termination_dir)


@patch("time.time", MagicMock(return_value=12345.6789))
def test_valid_and_empty_status():
    env = TestComponentActivityEnv(tempfile.mkdtemp())

    # Set a valid workspace status
    workspace_last_activity_timestamp = 9876.54321
    content = {
        "last_activity_timestamp": workspace_last_activity_timestamp,
    }
    env.write_status_file("workspace", content)

    # Do not set a web_terminal status

    result = component_activity_util.env_hook()
    assert result, "Env hook return none"
    assert result["workspace"], "workspace status should not be None"
    assert result["web_terminal"], "web_terminal status should not be None"
    workspace_result = result["workspace"]

    # Verify the workspace status matches input
    assert workspace_result["is_active"] == "INACTIVE"
    assert workspace_result["reason"] == "workspace last snapshot"
    assert workspace_result["timestamp"] == 12345.6789
    assert workspace_result["last_activity_at"] == workspace_last_activity_timestamp

    # Verify the web terminal status is empty
    web_terminal_result = result["web_terminal"]
    assert web_terminal_result["is_active"] == "ERROR"
    assert web_terminal_result["reason"] == "status file does not exist"
    assert web_terminal_result["timestamp"] == 12345.6789
    assert not web_terminal_result.get("last_activity_at")


@patch("time.time", MagicMock(return_value=12345.6789))
def test_error_status():
    env = TestComponentActivityEnv(tempfile.mkdtemp())
    # Valid status for workspace
    content = {
        "error": "custom error message",
    }
    env.write_status_file("workspace", content)

    # Invalid status for the web terminal
    env.write_status_file("web_terminal", {"invalid_property": 1234})

    result = component_activity_util.env_hook()
    assert result, "Env hook return none"
    assert result["workspace"], "workspace status should not be None"
    assert result["web_terminal"], "web_terminal status should not be None"
    workspace_result = result["workspace"]

    # Verify the workspace status is reported correctly
    assert workspace_result["is_active"] == "ERROR"
    assert workspace_result["reason"] == "custom error message"
    assert workspace_result["timestamp"] == 12345.6789
    assert not workspace_result.get("last_activity_at")

    # Verify an empty web terminal status
    web_terminal_result = result["web_terminal"]
    assert web_terminal_result["is_active"] == "ERROR"
    assert web_terminal_result["reason"] == "error parsing the status file"
    assert web_terminal_result["timestamp"] == 12345.6789
    assert not web_terminal_result.get("last_activity_at")
