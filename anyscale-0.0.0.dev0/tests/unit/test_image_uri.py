import re

import pytest

from anyscale._private.models.image_uri import ImageURI


class TestImageURI:
    @pytest.mark.parametrize(
        ("image_uri_str", "expected_name"),
        [
            ("docker.us.com/my/fakeimage:latest", "docker-us-com-my-fakeimage-latest"),
            ("library/ubuntu@sha256:45b23dee08", "library-ubuntu-sha256-45b23dee08"),
        ],
    )
    def test_image_uri_to_cluster_env_name(
        self, image_uri_str, expected_name,
    ):
        image_uri = ImageURI.from_str(image_uri_str)
        assert image_uri.to_cluster_env_name() == expected_name

    def test_empty_image_uri(self,):
        with pytest.raises(ValueError, match="image_uri cannot be empty."):
            ImageURI.from_str("")

    @pytest.mark.parametrize(
        ("image_uri_str", "is_legacy_cluster_env_image"),
        [("docker.us.com/my/fakeimage:laest", False), ("anyscale/image/name:5", True),],
    )
    def test_image_uri_is_legacy_cluster_env_image(
        self, image_uri_str, is_legacy_cluster_env_image
    ):
        assert (
            ImageURI.from_str(image_uri_str).is_cluster_env_image()
            == is_legacy_cluster_env_image
        )

    @pytest.mark.parametrize(
        ("image_uri", "valid"),
        [
            ("anyscale/cluster_env/default_cluster_env_2.9.3_py39:1", True),
            ("docker.io/libaray/ubuntu:latest", True),
            ("ubuntu:latest", True),
            ("python:3.8", True),
            ("myregistry.local:5000/testing/test-image:1.0.0", True),
            ("localhost:5000/myusername/myrepository:latest", True),
            ("localhost:5000/myusername/my/repository:latest", True),
            ("valid/withouttag", True),
            ("valid_name/withtag_and_digest:v2@sha213", True),
            ("valid_name/withtag_and_digest@sha213", True),
            ("valid_name/withtag_and_digest:@sha213", False),
            ("http://myregistry.local:5000/testing/test-image:1.0.0", False),
            (
                "us-docker.pkg.dev/anyscale-workspace-templates/workspace-templates/rag-dev-bootcamp-mar-2024:raynightly-py310",
                True,
            ),
            (
                "241673607239.dkr.ecr.us-west-2.amazonaws.com/aviary:release-endpoints_aica-e8873f9361e29289bcea2de47d967bdd5291ac46",
                True,
            ),
        ],
    )
    def test_image_uri_validation(self, image_uri: str, valid: bool):
        if valid:
            assert str(ImageURI.from_str(image_uri)) == image_uri
        else:
            with pytest.raises(
                ValueError,
                match=re.escape(
                    f"Invalid image URI: '{image_uri}'. Must be in the format: '[registry_host/]user_name/repository[:tag][@digest]'."
                ),
            ):
                ImageURI.from_str(image_uri)
