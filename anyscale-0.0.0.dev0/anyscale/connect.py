"""Anyscale connect implementation.

Here's an overview of how a connect call works. It goes through a few steps:
    1. Detecting the project and comparing build_id and compute_template_id
    2. Getting or creating a cluster if necessary.
    3. Acquiring a cluster lock via the Ray client (when not in multiclients mode)

Detecting the project: The project may be specified explicitly or
autodetected based on an initialized anyscale project in the
current working directory or one of its ancestor directories.
Otherwise the default project for the organization will be used.

Getting or creating a cluster: If a cluster name is passed in, anyscale
will start a cluster with that name unless the cluster is already running.
If the cluster is already running we compare the new cluster env build_id and
compute_template_id with the new cluster, if they match we connect, if they do
not match, we fail and require explicitly updating the cluster.

By default, multiple clients can connect to a cluster. If you want to
explicitly disable multiple client connects, set
ANYSCALE_ALLOW_MULTIPLE_CLIENTS=0 in the environment.
"""

import copy
from datetime import datetime, timezone
import inspect
import os
from pathlib import Path
import shlex
import subprocess
import sys
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import parse_qs, urlparse

from packaging import version
import requests
import yaml

from anyscale.api import configure_open_api_client_headers
from anyscale.authenticate import AuthenticationBlock, get_auth_api_client
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models.session import Session
from anyscale.conf import MINIMUM_RAY_VERSION
from anyscale.connect_utils.prepare_cluster import create_prepare_cluster_block
from anyscale.connect_utils.project import create_project_block
from anyscale.connect_utils.start_interactive_session import (  # pylint:disable=private-import
    _get_interactive_shell_frame,
    start_interactive_session_block,
)
import anyscale.project
from anyscale.sdk.anyscale_client.sdk import AnyscaleSDK
from anyscale.shared_anyscale_utils.util import slugify
from anyscale.util import PROJECT_NAME_ENV_VAR
from anyscale.utils.connect_helpers import AnyscaleClientContext, get_cluster


# Max number of auto created clusters.
MAX_CLUSTERS = 40

# The paths to exclude when syncing the working directory in runtime env.
EXCLUDE_DIRS = [".git", "__pycache__", "venv"]
EXCLUDE_PATHS = [".anyscale.yaml", "session-default.yaml"]

# The type of the dict that can be passed to create a cluster env.
# e.g., {"base_image": "anyscale/ray-ml:1.1.0-gpu"}
CLUSTER_ENV_DICT_TYPE = Dict[str, Union[str, List[str]]]

# The cluster compute type. It can either be a string, eg my_template or a dict,
# eg, {"cloud_id": "id-123" ...}
CLUSTER_COMPUTE_DICT_TYPE = Dict[str, Any]

# Commands used to build Ray from source. Note that intermediate stages will
# be cached by the app config builder.
BUILD_STEPS = [
    "git clone https://github.com/ray-project/ray.git",
    "curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor > bazel.gpg",
    "sudo mv bazel.gpg /etc/apt/trusted.gpg.d/",
    'echo "deb [arch=amd64] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list',
    "sudo apt-get update && sudo apt-get install -y bazel=3.2.0",
    'cd ray/python && sudo env "PATH=$PATH" python setup.py develop',
    "pip uninstall -y ray",
]


# Default docker images to use for connect clusters.
def _get_base_image(image: str, ray_version: str, cpu_or_gpu: str) -> str:
    py_version = "".join(str(x) for x in sys.version_info[0:2])
    if sys.version_info.major == 3 and sys.version_info.minor == 10:
        py_version = "310"
    if py_version not in ["36", "37", "38", "39", "310"]:
        raise ValueError(f"No default docker image for py{py_version}")
    return f"anyscale/{image}:{ray_version}-py{py_version}-{cpu_or_gpu}"


def _is_in_shell(frames: Optional[List[Any]] = None) -> bool:
    """
    Determines whether we are in a Notebook / shell.
    This is done by inspecting the first non-Anyscale related frame.
    If this is from an interactive terminal it will be either STDIN or IPython's Input.
    If connect() is being run from a file (like python myscript.py), frame.filename will equal "myscript.py".
    """
    fr = _get_interactive_shell_frame(frames)

    if fr is None:
        return False

    is_ipython = fr.filename.startswith("<ipython-input") and fr.filename.endswith(">")
    is_regular_python_shell: bool = fr.filename == "<stdin>"
    return is_regular_python_shell or is_ipython


def _is_running_on_anyscale_cluster() -> bool:
    return "ANYSCALE_SESSION_ID" in os.environ


def _redact_token(token: str) -> str:
    """Preserve a short prefix of the token, redact other characters."""
    preserve = 8
    n = len(token)
    if n <= preserve:
        return token
    redacted_len = 16
    return token[:preserve] + ("*" * (redacted_len - preserve))


class ClientBuilder:
    """This class lets you set cluster options and connect to Anyscale.

    It should not be constructed directly, but instead via ray.init("anyscale://") arguments
    exported at the package level.

    Examples:
        >>> # Raw client, creates new cluster on behalf of user
        >>> ray.init("anyscale://")

        >>> # Get or create a named cluster
        >>> ray.init("anyscale://my_named_cluster")

        >>> # Specify a previously created cluster environment
        >>> ray.init(
        ...   "anyscale://<cluster-name>?cluster_compute=compute:1",
        ...   cluster_env="prev_created_config:2",
        ...   autosuspend="2h")

        >>> # Create new cluster from local env / from scratch
        >>> ray.init("anyscale://<cluster-name>",
        ...   runtime_env={"working_dir": "~/dev/my-project-folder"}
        ... )

        >>> # Ray client connect is setup automatically
        >>> @ray.remote
        ... def my_func(value):
        ...   return value ** 2

        >>> # Remote functions are executed in the Anyscale cluster
        >>> print(ray.get([my_func.remote(x) for x in range(5)]))
        >>> [0, 1, 4, 9, 16]
    """

    def __init__(  # noqa: PLR0912
        self,
        address: Optional[str] = None,
        anyscale_sdk: AnyscaleSDK = None,
        subprocess: ModuleType = subprocess,
        requests: ModuleType = requests,
        _ray: Optional[ModuleType] = None,
        log: Optional[Any] = None,
        _os: ModuleType = os,
        _ignore_version_check: bool = False,
        auth_api_client: Optional[AuthenticationBlock] = None,
    ) -> None:

        # Class dependencies.
        self._anyscale_sdk: AnyscaleSDK = None
        self._credentials = None
        if auth_api_client is None:
            auth_api_client = get_auth_api_client()
        if log:
            self._log = log
        else:
            self._log = BlockLogger()
        if anyscale_sdk:
            self._anyscale_sdk = anyscale_sdk
        else:
            self._credentials = auth_api_client.credentials
            self._log.debug(
                "Using host {}".format(
                    anyscale.shared_anyscale_utils.conf.ANYSCALE_HOST
                )
            )
            redacted_token = _redact_token(self._credentials)
            self._log.debug(f"Using credentials {redacted_token}")
            self._anyscale_sdk = AnyscaleSDK(
                self._credentials, anyscale.shared_anyscale_utils.conf.ANYSCALE_HOST,
            )
            configure_open_api_client_headers(self._anyscale_sdk.api_client, "connect")
        api_client = auth_api_client.api_client

        configure_open_api_client_headers(api_client.api_client, "connect")
        anyscale_api_client = auth_api_client.anyscale_api_client
        self._api_client = api_client
        self._anyscale_api_client = anyscale_api_client
        if not _ray:
            try:
                import ray

                # Workaround for older versions of with ray that don't have the
                # fix for: https://github.com/ray-project/ray/issues/19840
                from ray.autoscaler import sdk  # noqa
            except ModuleNotFoundError:
                raise RuntimeError(
                    "Ray is not installed. Please install with: \n"
                    "pip install -U --force-reinstall `python -m anyscale.connect required_ray_version`"
                )
            _ray = ray
        self._ray: Any = _ray
        self._subprocess: Any = subprocess
        self._os: Any = _os
        self._requests: Any = requests
        self._in_shell = _is_in_shell()

        self._log.open_block("ParseArgs", block_title="Parsing Ray Client arguments")

        # Environment variables
        # If we are running in an anyscale cluster, or IGNORE_VERSION_CHECK is set,
        # skip the pinned versions
        if "IGNORE_VERSION_CHECK" in os.environ or _is_running_on_anyscale_cluster():
            _ignore_version_check = True
        self._ignore_version_check = _ignore_version_check

        if os.environ.get("ANYSCALE_COMPUTE_CONFIG") == "1":
            self._log.info(
                "All anyscale.connect clusters will be started with compute configs so "
                "ANYSCALE_COMPUTE_CONFIG=1 no longer needs to be specified."
            )

        # Determines whether the gRPC connection the server will be over SSL.
        self._secure: bool = os.environ.get("ANYSCALE_CONNECT_SECURE") != "0"
        if not self._secure:
            self._log.warning(
                "The connection between your machine and the cluster is *NOT* encrypted "
                "because the environment variable `ANYSCALE_CONNECT_SECURE=0` was specified. "
                "This is not recommended and will be deprecated in the near future."
            )

        # Builder args.
        self._project_dir: Optional[str] = None
        self._project_name: Optional[str] = None
        self._cloud_name: Optional[str] = None
        self._cluster_name: Optional[str] = None
        self._requirements: Optional[str] = None
        self._cluster_compute_name: Optional[str] = None
        self._cluster_compute_dict: Optional[CLUSTER_COMPUTE_DICT_TYPE] = None
        self._cluster_env_name: Optional[str] = None
        self._cluster_env_dict: Optional[CLUSTER_ENV_DICT_TYPE] = None
        self._cluster_env_revision: Optional[int] = None
        self._initial_scale: List[Dict[str, float]] = []
        # Will be overwritten to DEFAULT_AUTOSUSPEND_TIMEOUT if not set by user.
        self._autosuspend_timeout: Optional[int] = None
        self._run_mode: Optional[str] = None
        self._build_commit: Optional[str] = None
        self._build_pr: Optional[int] = None
        self._force_rebuild: bool = False
        self._job_config = self._ray.job_config.JobConfig()
        self._user_runtime_env: Dict[str, Any] = {}
        self._allow_public_internet_traffic: Optional[bool] = None
        self._ray_init_kwargs: Dict[str, Any] = {}
        # Override default run mode.
        if "ANYSCALE_LOCAL_DOCKER" in os.environ:
            self._run_mode = "local_docker"
            self._log.debug(
                "Using `run_mode=local_docker` since ANYSCALE_LOCAL_DOCKER is set"
            )

        # Whether to update the cluster when connecting to a fixed cluster.
        self._needs_update: bool = True
        self._parse_address(address)

    def _parse_cluster_project_name_in_address(self, address: str) -> Tuple[str, str]:
        """
        Parses cluster and project names from connection string as follows:
            address = "name1/name2" --> project_name = "name1", cluster_name = "name2"
            address = "name1/" --> project_name = "name1"
            address = "name1" --> cluster_name = "name1"
        Returns (project_name, cluster_name)
        """
        split_address = address.split("/")
        if len(split_address) == 1:
            # No "/" in address
            project_name = ""
            cluster_name = split_address[0]
        elif len(split_address) == 2:
            project_name = split_address[0]
            cluster_name = split_address[1]
        else:
            raise ValueError(
                f"The connection string `anyscale://{address}` has multiple subpaths. "
                "Please make sure the connection string is of the format `anyscale://project_name/cluster_name`."
            )
        return project_name, cluster_name

    def _parse_address(self, address: Optional[str]) -> None:
        """
        DEPRECATED, should be removed after deprecating the client builder.
        Parses the anyscale address and sets parameters on this builder.
        Eg, address="<cluster-name>?cluster_compute=my_template&autosuspend=5&cluster_env=bla:1&update=True
        """

        # The supported parameters that we can provide in the url.
        # e.g url="anyscale://ameer?param1=val1&param2=val2"
        CONNECT_URL_PARAMS = ["cluster_compute", "cluster_env", "autosuspend", "update"]

        self._project_name = os.environ.get(PROJECT_NAME_ENV_VAR)

        if address is None or not address:
            return
        parsed_result = urlparse(address)

        # Parse the cluster name. e.g., what is before the question mark in the url.
        project_name, cluster_name = self._parse_cluster_project_name_in_address(
            parsed_result.path
        )
        if cluster_name:
            self.session(cluster_name)
        self._project_name = project_name or self._project_name

        # parse the parameters (what comes after the question mark)
        # parsed_result.query here looks like "param1=val1&param2=val2"
        # params_dict looks like:
        # {'cluster_compute': ['my_template'], 'autosuspend': ['5'], 'cluster_env': ['bla:1']}.
        params_dict: Dict[str, Any] = parse_qs(parsed_result.query)
        for key, val in params_dict.items():
            if key == "autosuspend":
                self.autosuspend(minutes=int(val[0]))
            elif key == "cluster_env":
                self.cluster_env(val[0])
            elif key == "cluster_compute":
                self.cluster_compute(val[0])
            elif key == "update":
                self._needs_update = val[0] == "True" or val[0] == "true"
            else:
                raise ValueError(
                    "Provided parameter in the anyscale address is "
                    f"{key}. The supported parameters are: {CONNECT_URL_PARAMS}."
                )

    def _init_args(self, **kwargs) -> "ClientBuilder":  # noqa: PLR0912
        """
        Accepts arguments from ray.init when called with anyscale protocol,
        i.e. ray.init("anyscale://someCluster", arg1="thing", arg2="other").
        Ignores and raises a warning on unknown argument names.

        Arguments are set directly with method calls in _parse_arg_as_method.
        """
        unknown = []

        # request_resources arguments
        request_resources_cpus = kwargs.pop("request_cpus", None)
        request_resources_gpus = kwargs.pop("request_gpus", None)
        request_resources_bundles = kwargs.pop("request_bundles", None)

        # build_from_source arguments
        build_from_source_commit = kwargs.pop("git_commit", None)
        build_from_source_pr_id = kwargs.pop("github_pr_id", None)
        force_rebuild = kwargs.pop("force_rebuild", False)

        # project_dir arguments
        project_dir = kwargs.pop("project_dir", None)
        project_name = kwargs.pop("project_name", None)

        for arg_name, value in kwargs.items():
            if self._parse_arg_as_method(arg_name, value):
                continue
            elif arg_name == "autosuspend":
                self._parse_autosuspend(value)
            elif arg_name == "update":
                if not isinstance(value, bool):
                    # Extra cautious check -- make sure users don't pass
                    # None/"false" in
                    raise RuntimeError(
                        "The value passed for the `update` argument should "
                        f"be a boolean. Found {type(value)} instead."
                    )
                self._needs_update = value
            # Explicitly error on `num_cpus` and `num_gpus`, since it's likely
            # user confused with `request_cpus` and `request_gpus`
            elif arg_name == "num_cpus":
                raise RuntimeError(
                    "Invalid argument `num_cpus` for anyscale client. Did "
                    "you mean `request_cpus`?"
                )
            elif arg_name == "num_gpus":
                raise RuntimeError(
                    "Invalid argument `num_gpus` for anyscale client. Did "
                    "you mean `request_gpus`?"
                )
            elif arg_name == "allow_public_internet_traffic":
                if not isinstance(value, bool):
                    raise RuntimeError(
                        "The value passed for the `allow_public_internet_traffic` argument should "
                        f"be a boolean. Found {type(value)} instead."
                    )
                self._allow_public_internet_traffic = value
            elif self._forward_argument(arg_name, value):
                continue
            else:
                unknown.append(arg_name)

        if unknown:
            unknown_str = ", ".join(unknown)
            self._log.warning(
                f"Ignored, unsupported argument(s): {unknown_str}. This argument may not be "
                f"supported on ray {self._ray.__version__}. Try upgrading to a newer ray version "
                "or checking if this is a valid argument."
            )

        if (
            request_resources_cpus
            or request_resources_gpus
            or request_resources_bundles
        ):
            self.request_resources(
                num_cpus=request_resources_cpus,
                num_gpus=request_resources_gpus,
                bundles=request_resources_bundles,
            )

        if build_from_source_commit or build_from_source_pr_id:
            self.build_from_source(
                git_commit=build_from_source_commit,
                github_pr_id=build_from_source_pr_id,
                force_rebuild=force_rebuild,
            )

        if (
            self._user_runtime_env is None
            or self._user_runtime_env.get("working_dir") is None
        ):
            # This needs to be a warning message to not break users current usecases.
            # https://groups.google.com/a/anyscale.com/g/field-eng/c/4dAdqw4ORwU/m/eLYCCWZICAAJ?utm_medium=email&utm_source=footer&pli=1
            self._log.warning(
                "No working_dir specified! Files will only be uploaded to the cluster if a working_dir is provided or a project is detected. In the future, files will only be uploaded if working_dir is provided. "
                "To ensure files continue being imported going forward, set the working_dir in your runtime environment. "
                "See https://docs.ray.io/en/latest/handling-dependencies.html#runtime-environments."
            )

        if project_dir:
            self._log.warning(
                "The project_dir argument is deprecated and will be removed in April 2022. Instead, use the "
                "working_dir argument in a runtime environment. "
                "See https://docs.ray.io/en/latest/handling-dependencies.html#runtime-environments. "
                """Replace

                  ray.init("anyscale://...", project_dir=directory, ...)

                with

                  ray.init("anyscale://...", runtime_env={"working_dir": directory}, ...)
                """
            )
            self.project_dir(local_dir=project_dir, name=project_name)

        return self

    def _parse_autosuspend(self, value: Union[str, int]) -> None:
        """parses the value of autosuspend provided by the user.

        Autosuspend can be int interpreted as minutes or str -> "15m"/"2h" for 15 mins/2 hours.
        This function exists because self.autosuspend is used in the deprecated client builder
        (e.g., ray.client().autosuspend(...).connect()) and cannot be modified directly.
        Once we completely deprecate the client builder the old self.autosuspend can be updated.
        """
        if isinstance(value, str):
            # Autosuspend can take strings like "15" (minutes), "15m", and "2h"
            if value.endswith("m"):
                self.autosuspend(minutes=int(value[:-1]))
            elif value.endswith("h"):
                self.autosuspend(hours=int(value[:-1]))
            elif value == "-1":  # Setting autosuspend to "-1" disables it.
                self.autosuspend(enabled=False)
            else:
                self.autosuspend(minutes=int(value))
        elif value == -1:  # Setting autosuspend to -1 disables it.
            self.autosuspend(enabled=False)
        else:
            self.autosuspend(minutes=value)

    def _parse_arg_as_method(self, argument_name: str, argument_value: Any) -> bool:
        """
        Handle keyword arguments to ray.init that can be handled directly as
        a method call. For example, init(cloud="value") can be handled
        directly by self.cloud("value").

        Args:
            argument_name (str): Name of the argument (i.e. "cloud",
                "autosuspend")
            argument_value (Any): Corresponding value to the argument,
                (i.e. "anyscale_default", "8h")

        Returns:
            True if the argument can be handled directly by a method, False
            otherwise
        """
        if argument_name not in {
            "cloud",
            "cluster_compute",
            "cluster_env",
            "job_name",
            "namespace",
            "runtime_env",
            "run_mode",
        }:
            return False
        # convert argname: runtime_env -> env
        # We want to use the `env` function here for backwards compatibility,
        # but use `runtime_env` as the argument name since it's more clear
        # and consistent with ray's APIs.
        if argument_name == "runtime_env":
            argument_name = "env"
        getattr(self, argument_name)(argument_value)
        return True

    def _forward_argument(self, arg_name: str, value: Any) -> bool:
        """
        Fills self._ray_init_kwargs with any kwargs that match the signature of
        the current ray version's ray.init method.

        Returns True if the argument can be forwarded, false otherwise
        """
        connect_sig = inspect.signature(self._ray.util.connect)
        if "ray_init_kwargs" not in connect_sig.parameters:
            # Installed version of ray doesn't support forward init args
            # through connect
            return False

        init_sig = inspect.signature(self._ray.init)
        if arg_name in init_sig.parameters:
            self._ray_init_kwargs[arg_name] = value
            return True
        return False

    def env(self, runtime_env: Dict[str, Any]) -> "ClientBuilder":
        """Sets the custom user specified runtime environment dict.

        Args:
            runtime_env (Dict[str, Any]): a python dictionary with runtime environment
                specifications.

        Examples:
            >>> ray.init("anyscale://cluster_name", runtime_env={"pip": "./requirements.txt"})
            >>> ray.init("anyscale://cluster_name",
            ...     runtime_env={"working_dir": "/tmp/bla", "pip": ["chess"]})
            >>> ray.init("anyscale://cluster_name", runtime_env={"conda": "conda.yaml"})
        """
        if not isinstance(runtime_env, dict):
            raise TypeError("runtime_env argument type should be dict.")
        self._user_runtime_env = copy.deepcopy(runtime_env)
        return self

    def namespace(self, namespace: str) -> "ClientBuilder":
        """Sets the namespace in the job config of the started job.

        Args:
            namespace (str): the name of to give to this namespace.

        Example:
            >> ray.init("anyscale://cluster_name", namespace="training_namespace")
        """
        self._job_config.set_ray_namespace(namespace)
        return self

    def job_name(self, job_name: Optional[str] = None) -> "ClientBuilder":
        """Sets the job_name so the user can identify it in the UI.
        This name is only used for display purposes in the UI.

        Args:
            job_name (str): the name of this job, which will be shown in the UI.

        Example:
            >>> ray.init("anyscale://cluster_name", job_name="production_job")
        """
        current_time_str = datetime.now(timezone.utc).strftime("%m-%d-%Y_%H:%M:%S")
        if not job_name:
            script_name = sys.argv[0]
            if script_name:
                job_name = f"{os.path.basename(script_name)}_{current_time_str}"
            else:
                job_name = f"Job_{current_time_str}"
        self._job_config.set_metadata("job_name", job_name)
        return self

    def _rewrite_runtime_env_pip_as_list(self, runtime_env: Dict[str, Any]) -> None:
        """Parses and replaces the "pip" field of runtime_env with a List[str] if present."""
        if "pip" in runtime_env and isinstance(runtime_env["pip"], str):
            # We have been given a path to a requirements.txt file.
            pip_file = Path(runtime_env["pip"])
            if not pip_file.is_file():
                raise ValueError(f"{pip_file} is not a valid file")
            runtime_env["pip"] = pip_file.read_text().strip().split("\n")

    def _rewrite_runtime_env_conda_as_dict(self, runtime_env: Dict[str, Any]) -> None:
        """Parses and replaces the "conda" field of runtime_env with a Dict if present."""
        if "conda" in runtime_env and isinstance(runtime_env["conda"], str):
            yaml_file = Path(runtime_env["conda"])
            if yaml_file.suffix in (".yaml", ".yml"):
                if not yaml_file.is_file():
                    raise ValueError(f"Can't find conda YAML file {yaml_file}.")
                try:
                    runtime_env["conda"] = yaml.safe_load(yaml_file.read_text())
                except Exception as e:  # noqa: BLE001
                    raise ValueError(f"Failed to read conda file {yaml_file}: {e}.")

    def _pin_protobuf_in_runtime_env_if_needed(
        self, runtime_env: Dict[str, Any]
    ) -> None:
        """Pins protobuf to 3.20.1 in the "pip" and "conda" field for affected Ray versions.

        See https://github.com/anyscale/product/issues/12007 for details.
        """
        # Since Ray 1.10.0, pip installs are incremental, so the cluster's protobuf version
        # will be inherited and there's no need to add it to the "pip" field.
        if version.parse(self._ray.__version__) < version.parse("1.10.0"):
            self._rewrite_runtime_env_pip_as_list(runtime_env)
            if "pip" in runtime_env and isinstance(runtime_env["pip"], list):
                runtime_env["pip"].append("protobuf==3.20.1")

        # Fixed in Ray starting with Ray 1.13.0:
        # https://github.com/ray-project/ray/commit/6c8eb5e2ebde8db213ffb8722a0324077188e308
        if version.parse(self._ray.__version__) < version.parse("1.13.0"):
            self._rewrite_runtime_env_conda_as_dict(runtime_env)
            if (
                "conda" in runtime_env
                and isinstance(runtime_env["conda"], dict)
                and "dependencies" in runtime_env["conda"]
            ):
                for dep in runtime_env["conda"]["dependencies"]:
                    if (
                        isinstance(dep, dict)
                        and "pip" in dep
                        and isinstance(dep["pip"], list)
                    ):
                        dep["pip"].append("protobuf==3.20.1")

    def _set_runtime_env_in_job_config(self, project_dir: Optional[str]) -> None:
        """Configures the runtime env inside self._job_config.
        project_dir is None if using the default project.
        """

        runtime_env = copy.deepcopy(self._user_runtime_env)

        # There's no need to exclude files like ".anyscale.yaml"
        # if using the default project.
        project_dir_excludes = (
            [os.path.join(project_dir, path) for path in EXCLUDE_PATHS]
            if project_dir
            else []
        )

        if "working_dir" not in runtime_env and project_dir:
            # TODO(nikita): Remove logic of implying working dir from project dir
            runtime_env["working_dir"] = project_dir
        if "excludes" not in runtime_env:
            runtime_env["excludes"] = []
        runtime_env["excludes"] = (
            EXCLUDE_DIRS + runtime_env["excludes"] + project_dir_excludes
        )

        # Patch for https://github.com/ray-project/ray/issues/20876
        # If local pip or conda files are specified, read them here and rewrite
        # the runtime env to prevent FileNotFoundError in the Ray Client server.
        self._rewrite_runtime_env_pip_as_list(runtime_env)
        self._rewrite_runtime_env_conda_as_dict(runtime_env)

        self._pin_protobuf_in_runtime_env_if_needed(runtime_env)

        self._job_config.set_runtime_env(runtime_env)

    def _set_metadata_in_job_config(self, creator_id: Optional[str] = None) -> None:
        """
        Specify creator_id in job config. This is needed so the job
        can correctly be created in the database. Specify default job name
        if not user provided. This will be displayed in the UI.
        """
        # TODO(nikita): A customer can spoof this value and pretend to be someone else.
        # Fix this once we have a plan for verification.
        if creator_id is None:
            user = self._api_client.get_user_info_api_v2_userinfo_get().result
            creator_id = user.id

        self._job_config.set_metadata("creator_id", creator_id)
        if "job_name" not in self._job_config.metadata:
            self.job_name()

    def _fill_config_from_env(self, config_name: str) -> None:
        """
        Check if an environment variable corresponding to config_name is set,
        and if so try to configure the connection using that value. For
        example, if config_name is "job_name", then checks if the env var
        ANYSCALE_JOB_NAME is set. If it is, the calls self.job_name() on the
        value set for in the environment variable.
        """
        env_var_name = f"ANYSCALE_{config_name.upper()}"
        if env_var_name in os.environ:
            value = os.environ[env_var_name]
            self._log.info(
                f'Using "{value}" set in environment variable {env_var_name} to configure `{config_name}`.'
            )
            if config_name == "autosuspend":
                self._parse_autosuspend(value)
            else:
                getattr(self, config_name)(value)

    def _fill_unset_configs_from_env(self) -> None:
        """
        Fill unset configurations from environment variables. Currently
        supports the following configs: cloud, cluster_compute, cluster_env,
        job_name, and namespace.
        """
        if self._cloud_name is None:
            self._fill_config_from_env("cloud")

        # Only fill cluster_compute from environment if neither a name nor
        # a dict was passed
        cluster_compute_unset = (
            self._cluster_compute_name is None and self._cluster_compute_dict is None
        )
        if cluster_compute_unset:
            self._fill_config_from_env("cluster_compute")

        # Only fill cluster_env if neither a name nor a dict was passed
        cluster_env_unset = (
            self._cluster_env_name is None and self._cluster_env_dict is None
        )
        if cluster_env_unset:
            self._fill_config_from_env("cluster_env")

        if self._autosuspend_timeout is None:
            # override to env variable if available
            self._fill_config_from_env("autosuspend")

        if "job_name" not in self._job_config.metadata:
            self._fill_config_from_env("job_name")

        if self._job_config.ray_namespace is None:
            self._fill_config_from_env("namespace")

    def _bg_connect(self) -> Any:
        """
        Attach to the local ray cluster if we are running on the head node.
        """
        # This context is set from the outer job
        namespace = None
        # The user has directly called "ray.init(address="anyscale://...")
        # on the head node, so there is no outer job and no context.
        # We can still support this, but we need to pass the runtime env
        # in the job config just like in the ordinary anyscale.connect().
        self._job_config.set_runtime_env(self._user_runtime_env)

        # RAY_ADDRESS is set to anyscale://
        # We don't want the below ray.init to call into anyscale.connect
        del os.environ["RAY_ADDRESS"]
        return self._ray.init(  # This is a ClientContext object
            address="auto", job_config=self._job_config, namespace=namespace
        )

    def _set_serve_root_url_runtime_env(self, cluster: Session) -> None:
        # Sets SERVE_ROOT_URL_ENV_KEY to be the cluster's Serve URL. This will allow
        # users to pass the URL for Serve deployments with `DeploymentClass.url`
        # TODO(nikita): Update documentation once Ray 1.7 is released
        try:
            from ray.serve.constants import SERVE_ROOT_URL_ENV_KEY
        except ImportError:
            SERVE_ROOT_URL_ENV_KEY = "RAY_SERVE_ROOT_URL"

        try:
            self._user_runtime_env.setdefault("env_vars", {}).setdefault(
                SERVE_ROOT_URL_ENV_KEY, cluster.user_service_url.rstrip("/")
            )
        except Exception:  # noqa: BLE001
            self._log.warning(
                f"Unable to set {SERVE_ROOT_URL_ENV_KEY} in runtime environment. Please specify "
                "full Serve session URL for Serve deployments."
            )

    def connect(self) -> AnyscaleClientContext:
        """Connect to Anyscale using previously specified options.

        Examples:
            >>> ray.init("anyscale://cluster_name")

        WARNING: using a new cluster_compute/cluster_env when connecting to an
        active cluster will not work unless the user passes `update=True`. e.g.:
            >>> ray.init("anyscale://cluster_name?update=True")
        """

        feature_flag_on = self._api_client.check_is_feature_flag_on_api_v2_userinfo_check_is_feature_flag_on_get(
            "anyscale_connect_enabled_cli"
        ).result.is_on

        if not feature_flag_on:
            raise RuntimeError(
                "Anyscale Connect is disabled for your organization. Contact support for more details."
            )
        else:
            self._log.warning(
                "DEPRECATION WARNING: Anyscale Connect will be deprecated in future Anyscale versions. "
                "Please use workspaces: "
                "https://docs.anyscale.com/workspaces/get-started or Ray Jobs "
                "https://docs.anyscale.com/workspaces/interactive-development instead."
            )

        _allow_multiple_clients = (
            os.environ.get("ANYSCALE_ALLOW_MULTIPLE_CLIENTS") != "0"
        )
        self._log.info("Finished parsing arguments.", block_label="ParseArgs")
        self._log.close_block("ParseArgs")

        self._fill_unset_configs_from_env()

        if self._ray.util.client.ray.is_connected():
            raise RuntimeError(
                "Already connected to a Ray cluster, please "
                "run anyscale.connect in a new Python process."
            )

        # Allow the script to be run on an Anyscale cluster node as well.
        if _is_running_on_anyscale_cluster():
            # TODO(mattweber): Make background mode work with default projects.
            # This is a RayClientContext instead of an AnyscaleContext since we are connecting to the local cluster
            return self._bg_connect()  # type: ignore

        if self._run_mode == "local_docker":
            self._exec_self_in_local_docker()

        self._project_block = create_project_block(
            self._project_dir,
            self._project_name,
            cloud_name=self._cloud_name,
            cluster_compute_name=self._cluster_compute_name,
            cluster_compute_dict=self._cluster_compute_dict,
        )
        project_id = self._project_block.project_id
        project_dir = self._project_block.project_dir
        if project_dir and not self._project_name:
            # Warning when project dir provided or found in current directory and project name not provided
            # as input.
            # TODO(nikita): Remove after .anyscale.yaml is no longer supported
            self._log.warning(
                f"Project directory {project_dir} was detected. Using a project directory "
                "to set the Ray client project and working_dir has been deprecated, and this "
                "functionality will be removed in April 2022. To connect to an Anyscale cluster "
                "in a particular project, please instead specify the project name with "
                f'`ray.init("anyscale://{self._project_block.project_name}/{self._cluster_name if self._cluster_name else ""}")`. '
                "The project name can also be specified by setting the environment variable "
                f'`{PROJECT_NAME_ENV_VAR}="{self._project_block.project_name}"`. '
                "Otherwise the Ray client session will not be grouped to a particular project. "
                "From April 2022, the working_dir must also be specified to upload files and will "
                "not be implied from the project directory.\n"
            )

        self._prepare_cluster_block = create_prepare_cluster_block(
            project_id=project_id,
            cluster_name=self._cluster_name,
            autosuspend_timeout=self._autosuspend_timeout,
            allow_public_internet_traffic=self._allow_public_internet_traffic,
            needs_update=self._needs_update,
            cluster_compute_name=self._cluster_compute_name,
            cluster_compute_dict=self._cluster_compute_dict,
            cloud_name=self._cloud_name,
            build_pr=self._build_pr,
            force_rebuild=self._force_rebuild,
            build_commit=self._build_commit,
            cluster_env_name=self._cluster_env_name,
            cluster_env_dict=self._cluster_env_dict,
            cluster_env_revision=self._cluster_env_revision,
            ray=self._ray,
        )
        cluster_name = self._prepare_cluster_block.cluster_name

        cluster = self._get_cluster_or_die(project_id, cluster_name)
        self._set_serve_root_url_runtime_env(cluster)

        self._set_metadata_in_job_config()
        self._set_runtime_env_in_job_config(project_dir)

        self._interactive_session_block = start_interactive_session_block(
            cluster=cluster,
            job_config=self._job_config,
            allow_multiple_clients=_allow_multiple_clients,
            initial_scale=self._initial_scale,
            in_shell=self._in_shell,
            run_mode=self._run_mode,
            ray_init_kwargs=self._ray_init_kwargs,
            secure=self._secure,
            ignore_version_check=self._ignore_version_check,
            ray=self._ray,
            subprocess=self._subprocess,
        )

        return self._interactive_session_block.anyscale_client_context

    def cloud(self, cloud_name: str) -> "ClientBuilder":
        """Set the name of the cloud to be used.

        This sets the name of the cloud that your connect cluster will be started
        in by default. This is completely ignored if you pass in a cluster compute config.

        Args:
            cloud_name (str): Name of the cloud to start the cluster in.

        Examples:
            >>> ray.init("anyscale://cluster_name", cloud="aws_test_account")
        """
        self._cloud_name = cloud_name
        return self

    def project_dir(
        self, local_dir: str, name: Optional[str] = None
    ) -> "ClientBuilder":
        """DEPRECATED. project_dir should not be set by an argument,
        but it's okay for it to be set within this class for other reasons.

        Set the project directory path on the user's laptop.

        This sets the project code directory. If not specified, the project
        directory will be autodetected based on the current working directory.
        If no Anyscale project is found, the organization's default project will be used.
        In general the project directory will be synced to all nodes in the
        cluster as required by Ray, except for when the user passes
        "working_dir" in `.env()` in which case we sync the latter instead.

        Args:
            local_dir (str): path to the project directory.
            name (str): optional name to use if the project doesn't exist.

        Examples:
            >>> ray.init("anyscale://cluster_name", project_dir="~/my-proj-dir")
        """
        self._project_dir = os.path.abspath(os.path.expanduser(local_dir))
        self._project_name = name
        return self

    def session(self, cluster_name: str, update: bool = False) -> "ClientBuilder":
        """Set a fixed cluster name.

        Setting a fixed cluster name will create a new cluster if a cluster
        with cluster_name does not exist. Otherwise it will reconnect to an existing
        cluster.

        Args:
            cluster_name (str): fixed name of the cluster.
            update (bool): whether to update cluster configurations when
                connecting to an existing cluster. Note that this may restart
                the Ray runtime. By default update is set to False.

        Examples:
            >>> anyscale.session("prod_deployment", update=True).connect()
        """
        slugified_name = slugify(cluster_name)
        if slugified_name != cluster_name:
            self._log.error(
                f"Using `{slugified_name}` as the cluster name (instead of `{cluster_name}`)"
            )

        self._needs_update = update
        self._cluster_name = slugified_name

        return self

    def run_mode(self, run_mode: Optional[str] = None) -> "ClientBuilder":
        """Re-exec the driver program in the remote cluster or local docker.

        By setting ``run_mode("local_docker")``, you can tell Anyscale
        to re-exec the program driver in a local docker image, ensuring the
        driver environment will exactly match that of the remote cluster.

        You can also change the run mode by setting the ANYSCALE_LOCAL_DOCKER=1
        environment variable. Changing the run mode
        is only supported for script execution. Attempting to change the run
        mode in a notebook or Python shell will raise an error.

        Args:
            run_mode (str): either None, or "local_docker".

        Examples:
            >>> ray.init("anyscale://cluster_name")
        """
        if run_mode not in [None, "local_docker"]:
            raise ValueError(f"Unknown run mode {run_mode}")
        if self._in_shell and run_mode == "local_docker":
            raise ValueError("Local docker mode is not supported in Python shells.")
        self._run_mode = run_mode
        return self

    def base_docker_image(self, image_name: str) -> None:  # noqa: ARG002
        """[DEPRECATED] Set the docker image to use for the cluster.
        IMPORTANT: the Python minor version of the manually specified docker
        image must match the local Python version.
        Args:
            image_name (str): docker image name.
        Examples:
            >>> anyscale.base_docker_image("anyscale/ray-ml:latest").connect()
        """
        raise ValueError(
            "Anyscale connect doesn't support starting clusters with base docker images. "
            "Please specify a cluster_env instead. For example: "
            '`ray.init("anyscale://cluster_name?cluster_env=name:1")`'
        )

    def require(self, requirements: Union[str, List[str]]) -> None:  # noqa: ARG002
        """[DEPRECATED] Set the Python requirements for the cluster.
        Args:
            requirements: either be a list of pip library specifications, or
            the path to a requirements.txt file.
        Examples:
            >>> anyscale.require("~/proj/requirements.txt").connect()
            >>> anyscale.require(["gym", "torch>=1.4.0"]).connect()
        """
        raise ValueError(
            "Anyscale connect no longer accepts the `.require()` argument."
            "Please specify these requirements in your runtime env instead."
            'For example `ray.init("anyscale://my_cluster", runtime_env({"pip":["chess"'
            ',"xgboost"]})`.'
        )

    def cluster_compute(
        self, cluster_compute: Union[str, CLUSTER_COMPUTE_DICT_TYPE]
    ) -> "ClientBuilder":
        """Set the Anyscale cluster compute to use for the cluster.

        Args:
            cluster_compute: Name of the cluster compute
                or a dictionary to build a new cluster compute.
                For example "my-cluster-compute".


        Examples:
            >>> ray.init("anyscale://cluster_name?cluster_compute=my_cluster_compute")
            >>> ray.init("anyscale://cluster_name", cluster_compute="my_cluster_compute")
            >>> ray.init("anyscale://cluster_name", cluster_compute={"cloud_id": "1234", ... })

        WARNING:
            If you want to pass a dictionary cluster_compute please pass it using
            the `cluster_compute` argument. Passing it in the URL format will not work.
        """
        if isinstance(cluster_compute, str):
            self._cluster_compute_name = cluster_compute  # type: ignore
        elif isinstance(cluster_compute, dict):
            self._cluster_compute_dict = copy.deepcopy(cluster_compute)  # type: ignore
        else:
            raise TypeError(
                "cluster_compute should either be Dict[str, Any] or a string."
            )
        return self

    def cluster_env(
        self, cluster_env: Union[str, CLUSTER_ENV_DICT_TYPE]
    ) -> "ClientBuilder":
        """TODO(ameer): remove app_config below after a few releases.
        Set the Anyscale cluster environment to use for the cluster.

        IMPORTANT: the Python minor version of the manually specified cluster
        environment must match the local Python version, and the Ray version must
        also be compatible with the one on the client. for example, if your local
        laptop environment is using ray 1.4 and python 3.8, then the cluster environment
        ray version must be 1.4 and python version must be 3.8.

        Args:
            cluster_env: Name (and optionally revision) of
                the cluster environment or a dictionary to build a new cluster environment.
                For example "my_cluster_env:2" where the revision would be 2.
                If no revision is specified, use the latest revision.
                NOTE: if you pass a dictionary it will always rebuild a new cluster environment
                before starting the cluster.

        Examples:
            >>> ray.init("anyscale://cluster_name?cluster_env=prev_created_cluster_env:2")
            >>> ray.init("anyscale://cluster_name", cluster_env="prev_created_cluster_env:2")
            >>> ray.init("anyscale://cluster_name", cluster_env={"base_image": "anyscale/ray-ml:1.1.0-gpu"})

        WARNING:
            If you want to pass a dictionary cluster environment please pass it using
            the `cluster_env` argument. Passing it in the URL format will not work.
        """
        self.app_config(cluster_env)
        return self

    def app_config(
        self, cluster_env: Union[str, CLUSTER_ENV_DICT_TYPE],
    ) -> "ClientBuilder":
        """Set the Anyscale app config to use for the session.

        IMPORTANT: the Python minor version of the manually specified app
        config must match the local Python version, and the Ray version must
        also be compatible with the one on the client.

        Args:
            cluster_env: Name (and optionally revision) of
            the cluster environment or a dictionary to build a new cluster environment.
            For example "my_cluster_env:2" where the revision would be 2.
            If no revision is specified, use the latest revision.

        Examples:
            >>> anyscale.app_config("prev_created_config:2").connect()
        """

        if self._build_commit or self._build_pr:
            raise ValueError("app_config() conflicts with build_from_source()")
        if isinstance(cluster_env, str):
            components = cluster_env.rsplit(":", 1)  # type: ignore
            self._cluster_env_name = components[0]
            if len(components) == 1:
                self._cluster_env_revision = None
            else:
                self._cluster_env_revision = int(components[1])
        elif isinstance(cluster_env, dict):
            cluster_env_copy: CLUSTER_ENV_DICT_TYPE = copy.deepcopy(cluster_env)  # type: ignore
            self._cluster_env_name = cluster_env_copy.pop("name", None)  # type: ignore
            self._cluster_env_dict = cluster_env_copy
        else:
            raise TypeError("The type of cluster_env must be either a str or a dict.")
        return self

    def download_results(
        self, *, remote_dir: str, local_dir: str  # NOQA: ARG002
    ) -> None:
        """Specify a directory to sync down from the cluster head node.

        IMPORTANT: the data is downloaded immediately after this call.
            `download_results` must not be called with `.connect()`. See examples below.

        Args:
            remote_dir (str): the result dir on the head node.
            local_dir (str): the local path to download the results to.

        Examples:
            >>> ray.client("anyscale://cluster_name")
            ...   .download_results(
            ...       local_dir="~/ray_results", remote_dir="/home/ray/proj_output")
            >>> ray.client("anyscale://").download_results(
            ...       local_dir="~/ray_results", remote_dir="/home/ray/proj_output")
            >>> anyscale.download_results(
            ...       local_dir="~/ray_results", remote_dir="/home/ray/proj_output")
        """
        if not self._ray.util.client.ray.is_connected():
            raise RuntimeError(
                "Not connected to cluster. Please re-run this after "
                'to a cluster via ray.client("anyscale://...").connect()'
            )

        raise RuntimeError("Downloading results is not supported on anyscale V2")

    def autosuspend(
        self,
        enabled: bool = True,
        *,
        hours: Optional[int] = None,
        minutes: Optional[int] = None,
    ) -> "ClientBuilder":
        """Configure or disable cluster autosuspend behavior.

        The cluster will be autosuspend after the specified time period. By
        default, cluster auto terminate after one hour of idle.

        Args:
            enabled (bool): whether autosuspend is enabled.
            hours (int): specify idle time in hours.
            minutes (int): specify idle time in minutes. This is added to the
                idle time in hours.

        Examples:
            >>> ray.init("anyscale://cluster_name", autosuspend=-1) # to disable
            >>> ray.init("anyscale://cluster_name", autosuspend="2h")
        """
        if enabled:
            if hours is None and minutes is None:
                timeout = None
            else:
                timeout = 0
                if hours is not None:
                    timeout += hours * 60
                if minutes is not None:
                    timeout += minutes
        else:
            timeout = -1
        self._autosuspend_timeout = timeout
        return self

    def allow_public_internet_traffic(self, enabled: bool = False) -> "ClientBuilder":
        """Enable or disable public internet trafic for Serve deployments.

        Disabling public internet traffic causes the Serve deployments running on this cluster
        to be put behind an authentication proxy. By default, clusters will be started with
        Serve deployments rejecting internet traffic unless an authentication token is included
        in the cookies.

        Args:
            enabled (bool): whether public internet traffic is accepted for Serve deployments

        Examples:
            >>> ray.init("anyscale://cluster_name", allow_public_internet_traffic=True)
        """
        self._allow_public_internet_traffic = enabled
        return self

    def build_from_source(
        self,
        *,
        git_commit: Optional[str] = None,
        github_pr_id: Optional[int] = None,
        force_rebuild: bool = False,
    ) -> "ClientBuilder":
        """Build Ray from source for the cluster runtime.

        This is an experimental feature.

        Note that the first build for a new base image might take upwards of
        half an hour. Subsequent builds will have cached compilation stages.

        Args:
            git_commit (Optional[str]): If specified, try to checkout the exact
                git commit from the Ray master branch. If pull_request_id is
                also specified, the commit may be from the PR branch as well.
            github_pr_id (Optional[int]): Specify the pull request id to use.
                If no git commit is specified, the latest commit from the pr
                will be used.
            force_rebuild (bool): Force rebuild of the app config.

        Examples:
            >>> anyscale
            ...   .build_from_source(git_commit="f1e293c", github_pr_id=12345)
            ...   .connect()
        """
        if self._cluster_env_name:
            raise ValueError("cluster_env() conflicts with build_from_source()")
        self._build_commit = git_commit
        self._build_pr = github_pr_id
        self._force_rebuild = force_rebuild
        return self

    def request_resources(
        self,
        *,
        num_cpus: Optional[int] = None,
        num_gpus: Optional[int] = None,
        bundles: Optional[List[Dict[str, float]]] = None,
    ) -> "ClientBuilder":
        """Configure the initial resources to scale to.

        The cluster will immediately attempt to scale to accomodate the
        requested resources, bypassing normal upscaling speed constraints.
        The requested resources are pinned and exempt from downscaling.

        Args:
            num_cpus (int): number of cpus to request.
            num_gpus (int): number of gpus to request.
            bundles (List[Dict[str, float]): resource bundles to
                request. Each bundle is a dict of resource_name to quantity
                that can be allocated on a single machine. Note that the
                ``num_cpus`` and ``num_gpus`` args simply desugar into
                ``[{"CPU": 1}] * num_cpus`` and ``[{"GPU": 1}] * num_gpus``
                respectively.

        Examples:
            >>> ray.init("anyscale://cluster_name", request_cpus=200, request_gpus=30)
            >>> ray.init("anyscale://cluster_name", request_cpus=8,
            ...     request_bundles=[{"GPU": 8}, {"GPU": 8}, {"GPU": 1}],
            ... )
        """
        to_request: List[Dict[str, float]] = []
        if num_cpus:
            to_request += [{"CPU": 1}] * num_cpus
        if num_gpus:
            to_request += [{"GPU": 1}] * num_gpus
        if bundles:
            to_request += bundles
        self._initial_scale = to_request
        return self

    def _get_cluster_or_die(self, project_id: str, session_name: str) -> Session:
        """Query Anyscale for the given cluster's metadata."""
        cluster_found = get_cluster(self._anyscale_sdk, project_id, session_name)
        if not cluster_found:
            raise RuntimeError(f"Failed to locate cluster: {session_name}")
        return cluster_found

    def _exec_self_in_local_docker(self) -> None:
        """Run the current main file in a local docker image."""
        cur_file = os.path.abspath(sys.argv[0])
        docker_image = _get_base_image("ray-ml", MINIMUM_RAY_VERSION, "cpu")
        command = [
            "docker",
            "run",
            "--env",
            "ANYSCALE_HOST={}".format(
                anyscale.shared_anyscale_utils.conf.ANYSCALE_HOST
            ),
            "--env",
            f"ANYSCALE_CLI_TOKEN={self._credentials}",
            "-v",
            f"{cur_file}:/user_main.py",
            "--entrypoint=/bin/bash",
            docker_image,
            "-c",
            "python /user_main.py {}".format(
                " ".join([shlex.quote(x) for x in sys.argv[1:]])
            ),
        ]
        self._log.debug("Running", command)
        self._subprocess.check_call(command)
        self._os._exit(0)  # pylint:disable=private-use  # noqa: SLF001


# This implements the following utility function for users:
# $ pip install -U `python -m anyscale.connect required_ray_version`
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "required_ray_version":
        # TODO(ilr/nikita) Make this >= MINIMUM VERSION when we derive MINIMUM VERSION
        # from the backend.
        print(f"ray=={MINIMUM_RAY_VERSION}")
    else:
        raise ValueError("Unsupported argument.")
