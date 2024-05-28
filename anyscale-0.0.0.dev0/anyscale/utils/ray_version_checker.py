import sys

from anyscale.cli_logger import BlockLogger
from anyscale.util import get_wheel_url


def detect_python_minor_version() -> str:
    return f"{sys.version_info[0]}.{sys.version_info[1]}"


def check_required_ray_version(
    logger: BlockLogger,
    ray_version: str,
    ray_commit: str,
    required_ray_version: str,
    required_ray_commit: str,
    ignore_version_check: bool,
) -> None:
    if ray_commit == "{{RAY_COMMIT_SHA}}":
        logger.warning(
            "Ray version checking is skipped because Ray is likely built locally for development. "
            "Compatibility between Ray and Anyscale connect is not guaranteed."
        )
        return

    if ray_version != required_ray_version:
        msg = "The local ray installation has version {}, but {} is required.".format(
            ray_version, required_ray_version
        )
    elif ray_commit != required_ray_commit:
        msg = "The local ray installation has commit {}, but {} is required.".format(
            ray_commit[:7], required_ray_commit[:7]
        )
    else:
        # Version and commit matches.
        return

    msg = (
        "{}\nPlease install the required "
        "Ray version by running:\n\t`pip uninstall ray -y && pip install -U {}`\nTo unsafely "
        "ignore this check, set IGNORE_VERSION_CHECK=1.".format(
            msg, get_wheel_url(required_ray_commit, required_ray_version),
        )
    )
    if ignore_version_check:
        logger.debug(msg)
    else:
        raise ValueError(msg)
