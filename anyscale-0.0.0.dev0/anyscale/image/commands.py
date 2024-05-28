from anyscale._private.sdk import sdk_command
from anyscale.image._private.image_sdk import ImageSDK


_IMAGE_SDK_SINGLETON_KEY = "image_sdk"

_BUILD_FROM_CONTAINERFILE_EXAMPLE = """
import anyscale

containerfile = '''
FROM anyscale/ray:2.21.0-py39
RUN pip install --no-cache-dir pandas
'''

image_uri: str = anyscale.image.build(containerfile, name="mycoolimage")
"""


@sdk_command(
    _IMAGE_SDK_SINGLETON_KEY,
    ImageSDK,
    doc_py_example=_BUILD_FROM_CONTAINERFILE_EXAMPLE,
    arg_docstrings={
        "name": "The name of the image.",
        "containerfile": "The content of the Containerfile.",
    },
)
def build(containerfile: str, *, name: str, _sdk: ImageSDK) -> str:
    build_id = _sdk.build_image_from_containerfile(name, containerfile)
    image_uri = _sdk.get_image_uri_from_build_id(build_id)
    if image_uri:
        return image_uri.image_uri
    raise RuntimeError(
        f"This is a bug! Failed to get image uri for build {build_id} that just created."
    )
