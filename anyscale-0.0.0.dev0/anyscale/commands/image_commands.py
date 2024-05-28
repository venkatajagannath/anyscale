from typing import IO

import click

import anyscale


@click.group(
    "image", help="Manage images to define dependencies on Anyscale.",
)
def image_cli() -> None:
    pass


@image_cli.command(
    name="build", help=("Build an image from a Containerfile."),
)
@click.option(
    "--containerfile",
    "-f",
    help="Path to the Containerfile.",
    type=click.File("rb"),
    required=True,
)
@click.option(
    "--name",
    "-n",
    help="Name for the image. If the image with the same name already exists, a new version will be built. Otherwise, a new image will be created.",
    required=True,
    type=str,
)
def build(containerfile: IO[bytes], name: str) -> None:
    containerfile_str = containerfile.read().decode("utf-8")
    image_uri = anyscale.image.build(containerfile_str, name=name)
    print(f"Image built successfully with URI: {image_uri}")
