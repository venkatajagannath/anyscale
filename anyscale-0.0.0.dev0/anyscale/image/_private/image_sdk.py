import os
from typing import List, Optional

from anyscale._private.anyscale_client.common import AnyscaleClientInterface
from anyscale._private.models.image_uri import ImageURI
from anyscale._private.sdk.base_sdk import BaseSDK
from anyscale.cli_logger import BlockLogger
from anyscale.sdk.anyscale_client.models.cluster_environment_build import (
    ClusterEnvironmentBuild,
)
from anyscale.sdk.anyscale_client.models.cluster_environment_build_status import (
    ClusterEnvironmentBuildStatus,
)


ENABLE_IMAGE_BUILD_FOR_TRACKED_REQUIREMENTS = (
    os.environ.get("ANYSCALE_ENABLE_IMAGE_BUILD_FOR_TRACKED_REQUIREMENTS", "0") == "1"
)


class ImageSDK(BaseSDK):
    def __init__(
        self,
        *,
        logger: Optional[BlockLogger] = None,
        client: Optional[AnyscaleClientInterface] = None,
    ):
        super().__init__(logger=logger, client=client)
        self._enable_image_build_for_tracked_requirements = (
            ENABLE_IMAGE_BUILD_FOR_TRACKED_REQUIREMENTS
        )

    @property
    def enable_image_build_for_tracked_requirements(self) -> bool:
        return self._enable_image_build_for_tracked_requirements

    def get_default_image(self) -> str:
        return self.client.get_default_build_id()

    def get_image_build(self, build_id: str) -> Optional[ClusterEnvironmentBuild]:
        return self.client.get_cluster_env_build(build_id)

    def build_image_from_containerfile(self, name: str, containerfile: str) -> str:
        return self.client.get_cluster_env_build_id_from_containerfile(
            cluster_env_name=name, containerfile=containerfile, anonymous=False
        )

    def build_image_from_requirements(
        self, name: str, base_build_id: str, requirements: List[str]
    ):
        if requirements:
            base_build = self.client.get_cluster_env_build(base_build_id)
            if (
                base_build
                and base_build.status == ClusterEnvironmentBuildStatus.SUCCEEDED
                and base_build.docker_image_name
            ):
                self.logger.info(f"Using tracked python packages: {requirements}")
                lines = [
                    "# syntax=docker/dockerfile:1",
                    f"FROM {base_build.docker_image_name}",
                ]
                for requirement in requirements:
                    lines.append(f'RUN pip install "{requirement}"')
                return self.build_image_from_containerfile(name, "\n".join(lines))
            else:
                raise RuntimeError(
                    f"Base build {base_build_id} is not a successful build."
                )
        else:
            return base_build_id

    def registery_image(self, image_uri: str) -> str:
        image_uri_checked = ImageURI.from_str(image_uri_str=image_uri)
        return self.client.get_cluster_env_build_id_from_image_uri(
            image_uri=image_uri_checked
        )

    def get_image_uri_from_build_id(self, build_id: str) -> Optional[ImageURI]:
        return self.client.get_cluster_env_build_image_uri(
            cluster_env_build_id=build_id
        )
