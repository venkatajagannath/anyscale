from typing import Tuple

import pytest

from anyscale._private.anyscale_client.fake_anyscale_client import FakeAnyscaleClient
from anyscale._private.models.image_uri import ImageURI
from anyscale.image._private.image_sdk import ImageSDK


@pytest.fixture()
def sdk_with_fake_client() -> Tuple[ImageSDK, FakeAnyscaleClient]:
    fake_client = FakeAnyscaleClient()
    return ImageSDK(client=fake_client), fake_client


class TestBuildImageFromRequirements:
    def test_build_image_from_requirements(
        self, sdk_with_fake_client: Tuple[ImageSDK, FakeAnyscaleClient],
    ):
        sdk, fake_client = sdk_with_fake_client
        build_id = "mybaseimageid"
        image_uri = ImageURI.from_str("docker.io/fake/default:latest")
        image_name = "bldname123"
        fake_client.set_image_uri_mapping(
            image_uri, build_id,
        )

        expected_containerfile = "\n".join(
            [
                "# syntax=docker/dockerfile:1",
                f"FROM {image_uri}",
                'RUN pip install "requests"',
                'RUN pip install "flask"',
            ]
        )

        fake_client.set_containerfile_mapping(
            expected_containerfile, build_id="my_new_build"
        )

        actual_build_id = sdk.build_image_from_requirements(
            image_name, build_id, requirements=["requests", "flask"],
        )

        assert actual_build_id == "my_new_build"
