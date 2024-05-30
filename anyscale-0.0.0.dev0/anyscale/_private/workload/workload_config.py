from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from anyscale._private.models import ImageURI, ModelBase
from anyscale.compute_config.models import ComputeConfig


@dataclass(frozen=True)
class WorkloadConfig(ModelBase):
    name: Optional[str] = field(
        default=None, metadata={"docstring": "Should be overwritten by subclass."}
    )

    def _validate_name(self, name: Optional[str]):
        if name is not None and not isinstance(name, str):
            raise TypeError("'name' must be a string.")

    image_uri: Optional[str] = field(
        default=None,
        metadata={
            "docstring": "URI of an existing image. Exclusive with `containerfile`."
        },
    )

    def _validate_image_uri(self, image_uri: Optional[str]):
        if image_uri is not None and not isinstance(image_uri, str):
            raise TypeError(f"'image_uri' must be an str but it is {type(image_uri)}.")
        if image_uri is not None:
            ImageURI.from_str(image_uri)

    containerfile: Optional[str] = field(
        default=None,
        repr=False,
        metadata={
            "docstring": "The file path to a containerfile that will be built into an image before running the workload. Exclusive with `image_uri`."
        },
    )

    def _validate_containerfile(self, containerfile: Optional[str]):
        if containerfile is not None and not isinstance(containerfile, str):
            raise TypeError("'containerfile' must be a string.")

    compute_config: Union[ComputeConfig, Dict, str, None] = field(
        default=None,
        metadata={
            "docstring": "The name of an existing registered compute config or an inlined ComputeConfig object."
        },
    )

    def _validate_compute_config(
        self, compute_config: Union[ComputeConfig, Dict, str, None]
    ) -> Union[None, str, ComputeConfig]:
        if compute_config is None or isinstance(compute_config, str):
            return compute_config

        if isinstance(compute_config, dict):
            compute_config = ComputeConfig.from_dict(compute_config)
        if not isinstance(compute_config, ComputeConfig):
            raise TypeError(
                "'compute_config' must be a string, ComputeConfig, or corresponding dict"
            )

        return compute_config

    working_dir: Optional[str] = field(
        default=None,
        repr=False,
        metadata={
            "docstring": "Directory that will be used as the working directory for the application. If a local directory is provided, it will be uploaded to cloud storage automatically. When running inside a workspace, this defaults to the current working directory ('.')."
        },
    )

    def _validate_working_dir(self, working_dir: Optional[str]):
        if working_dir is not None and not isinstance(working_dir, str):
            raise TypeError("'working_dir' must be a string.")

    excludes: Optional[List[str]] = field(
        default=None,
        repr=False,
        metadata={
            "docstring": "A list of file path globs that will be excluded when uploading local files for `working_dir`."
        },
    )

    def _validate_excludes(self, excludes: Optional[List[str]]):
        if excludes is not None and (
            not isinstance(excludes, list)
            or not all(isinstance(e, str) for e in excludes)
        ):
            raise TypeError("'excludes' must be a list of strings.")

    requirements: Optional[Union[str, List[str]]] = field(
        default=None,
        repr=False,
        metadata={
            "docstring": "A list of requirements or a path to a `requirements.txt` file for the workload. When running inside a workspace, this defaults to the workspace-tracked requirements."
        },
    )

    def _validate_requirements(self, requirements: Optional[Union[str, List[str]]]):
        if requirements is None or isinstance(requirements, str):
            return

        if not isinstance(requirements, list) or not all(
            isinstance(r, str) for r in requirements
        ):
            raise TypeError(
                "'requirements' must be a string (file path) or list of strings."
            )

    env_vars: Optional[Dict[str, str]] = field(
        default=None,
        repr=True,
        metadata={
            "docstring": "A dictionary of environment variables that will be set for the workload."
        },
    )

    def _validate_env_vars(self, env_vars: Optional[Dict[str, str]]):
        if env_vars is not None and (
            not isinstance(env_vars, dict)
            or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in env_vars.items()
            )
        ):
            raise TypeError("'env_vars' must be a Dict[str, str].")

    py_modules: Optional[List[str]] = field(
        default=None,
        repr=True,
        metadata={
            "docstring": "A list of local directories that will be uploaded and added to the Python path."
        },
    )

    def _validate_py_modules(self, py_modules: Optional[List[str]]):
        if py_modules is not None and (
            not isinstance(py_modules, list)
            or not all(isinstance(m, str) for m in py_modules)
        ):
            raise TypeError("'py_modules' must be a list of strings.")
