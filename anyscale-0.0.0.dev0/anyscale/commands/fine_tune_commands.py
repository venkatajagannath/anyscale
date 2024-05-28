from typing import Optional

import click

from anyscale.controllers.fine_tune_controller import FineTuneController
from anyscale.models.fine_tune_model import FineTuneConfig


@click.group(
    "fine-tuning", help="Interact with fine-tuning jobs running on Anyscale.",
)
def fine_tune_cli() -> None:
    pass


@fine_tune_cli.command(name="submit")
@click.argument("base-model", required=True)
@click.option("--train-file", required=True, help="The path of the training file.")
@click.option(
    "--valid-file",
    required=False,
    default=None,
    help="The path of the validation file.",
)
@click.option("--cloud-id", required=True, help="The id of the cloud")
@click.option(
    "--suffix",
    required=False,
    default=None,
    help="The suffix of the fine-tuned model.",
)
@click.option(
    "--version",
    required=False,
    default=None,
    help=(
        "The version of ray-llm expected to be used for the fine-tuned model. "
        "If not specified, the latest version will be used."
    ),
)
@click.option(
    "--instance-type",
    required=False,
    default=None,
    help=(
        "The instance type to use for the fine-tuning job. "
        "Please refer to docs at https://docs.anyscale.com/endpoints/fine-tuning/get-started for available instance types."
        "If not specified, the default instance type will be used."
    ),
)
def submit(
    base_model: str,
    train_file: str,
    valid_file: Optional[str],
    cloud_id: str,
    suffix: Optional[str],
    version: Optional[str],
    instance_type: Optional[str],
) -> None:
    """
    Submits a fine-tuning job.

    Example usage:

        anyscale fine-tuning submit --model meta-llama/Llama-2-7b-chat-hf --train-file train.jsonl --cloud-id CLOUD_ID
    """
    fine_tune_controller = FineTuneController()
    config = FineTuneConfig(
        base_model=base_model,
        train_file=train_file,
        valid_file=valid_file,
        cloud_id=cloud_id,
        suffix=suffix,
        version=version,
        instance_type=instance_type,
    )
    fine_tune_controller.fine_tune(config=config)
