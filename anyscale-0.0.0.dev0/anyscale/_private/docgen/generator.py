import ast
from dataclasses import dataclass, fields
import inspect
import typing
from typing import Any, Callable, Dict, List, Optional, Type, Union

import click
import yaml

from anyscale._private.models.model_base import ModelBaseType, ModelEnumType


ModelType = Union[ModelBaseType, ModelEnumType]

CLI_OPTIONS_TO_SKIP = {"help", "service_id", "project_id"}
FILE_EXTENSION = ".md"

CUSTOMER_HOSTED_ANCHOR = "#customer-hosted-only"
CUSTOMER_HOSTED_HEADER = """\
#### Customer-hosted cloud features {#customer-hosted-only}
:::note
Some features are only available on customer-hosted clouds. Reach out to preview-help@anyscale.com for info.
:::"""

CUSTOMER_HOSTED_QUALIFIER = (
    "Only available on [customer-hosted clouds](#customer-hosted-only)."
)


@dataclass
class Module:
    title: str
    filename: str
    cli_prefix: str
    cli_commands: List[click.Command]
    sdk_prefix: str
    sdk_commands: List[Callable]
    models: List[ModelType]


class MarkdownGenerator:
    """Generates markdown reference documentations for a list of CLI modules."""

    def __init__(self, modules: List[Module]):
        self._modules = modules

        # Used as an index to generate anchor links to models.
        self._model_type_to_filename: Dict[ModelType, str] = {}
        for m in modules:
            if not m.filename.endswith(FILE_EXTENSION):
                raise ValueError(f"All file names must be in '{FILE_EXTENSION}'.")

            for model in m.models:
                filename_no_extension = m.filename[: -len(FILE_EXTENSION)]
                self._model_type_to_filename[model] = filename_no_extension

    def generate(self) -> Dict[str, str]:
        """Generate documentation for all of the input modules.

        Returns a dictionary of filename to generated file contents.

        Each module will contain three sections:
            - Models
            - CLI
            - SDK

        An index.md file will also be generated containing a table linking to all
        top-level sections for each module.
        """

        output_files: Dict[str, str] = {}
        index = "# Platform API\n\n"
        for m in self._modules:
            title_anchor = m.title.lower().replace(" ", "-")
            filename_no_extension = m.filename[: -len(FILE_EXTENSION)]

            output = "import Tabs from '@theme/Tabs';\n"
            output += "import TabItem from '@theme/TabItem';\n\n"
            output += f"# {m.title} API Reference\n\n"
            output += CUSTOMER_HOSTED_HEADER + "\n\n"
            index += f"- [{m.title} API Reference]({filename_no_extension})\n"
            index += f"  - [{m.title} Models]({filename_no_extension}#{title_anchor}-models)\n"

            output += f"## {m.title} Models\n"
            for t in m.models:
                output += "\n" + self._gen_markdown_for_model(t)

            if len(m.cli_commands) > 0:
                output += f"## {m.title} CLI\n"
                index += (
                    f"  - [{m.title} CLI]({filename_no_extension}#{title_anchor}-cli)\n"
                )
                for t in m.cli_commands:
                    output += "\n" + self._gen_markdown_for_cli_command(
                        t, cli_prefix=m.cli_prefix
                    )

            if len(m.sdk_commands) > 0:
                output += f"## {m.title} SDK\n"
                index += (
                    f"  - [{m.title} SDK]({filename_no_extension}#{title_anchor}-sdk)\n"
                )
                for t in m.sdk_commands:
                    output += "\n" + self._gen_markdown_for_sdk_command(
                        t, sdk_prefix=m.sdk_prefix
                    )

            output_files[m.filename] = output

        output_files["index.md"] = index
        return output_files

    def _get_anchor(self, t: ModelType):
        """Get a markdown anchor (link) to the given type's docs."""
        filename = self._model_type_to_filename[t]
        return f"{filename}#{t.__name__.lower()}"

    def _type_container_to_string(self, t: typing.Type) -> str:
        """Return a str representation of a type hint."""
        origin, args = typing.get_origin(t), typing.get_args(t)
        assert origin is not None and args is not None

        if origin is Union:
            return " | ".join(self._model_type_to_string(arg) for arg in args)

        if origin is dict:
            arg_str = ", ".join([self._model_type_to_string(arg) for arg in args])
            if args:
                return f"Dict[{arg_str}]"
            else:
                return "Dict"

        if origin is list:
            arg_str = ", ".join([self._model_type_to_string(arg) for arg in args])
            if arg_str:
                return f"List[{arg_str}]"
            else:
                return "List"

        raise NotImplementedError(f"Unhandled type: {t}")

    def _model_type_to_string(self, t: Type):  # noqa: PLR0911
        """Return a str representation of any Python type.

        Any unrecognized types will be raise an error (handling must be explicitly added).
        """
        if t is Any:
            return "Any"
        if t is str:
            return "str"
        if t is bool:
            return "bool"
        if t is int:
            return "int"
        if t is float:
            return "float"
        if t is type(None):
            return "None"
        if typing.get_origin(t) is not None:
            return self._type_container_to_string(t)
        if isinstance(t, (ModelBaseType, ModelEnumType)):
            return f"[{t.__name__}]({self._get_anchor(t)})"

        # Avoid poor rendering of unhandled types.
        raise NotImplementedError(
            f"Unhandled type: {t}. Either this type should not be in our public APIs, or you must add handling for it to the doc generator."
        )

    def _gen_example_tabs(self, t: Union[Callable, ModelBaseType]) -> str:
        """Generate a tab section that contains yaml, python, and/or CLI examples for the type.

        The examples are pulled from magic attributes:
            - __doc_yaml_example__ (required for models ending with "Config")
            - __doc_py_example__ (required in all cases)
            - __doc_cli_example__ (required for models)
        """
        yaml_example: Optional[str] = getattr(t, "__doc_yaml_example__", None)
        py_example: Optional[str] = getattr(t, "__doc_py_example__", None)
        cli_example: Optional[str] = getattr(t, "__doc_cli_example__", None)

        if isinstance(t, ModelBaseType):
            if not py_example:
                raise ValueError(
                    f"Model '{t.__name__}' is missing a '__doc_py_example__'."
                )
            if t.__name__.endswith("Config") and not yaml_example:
                raise ValueError(
                    f"Config model '{t.__name__}' is missing a '__doc_yaml_example__'."
                )
        elif not py_example:
            raise ValueError(
                f"SDK command '{t.__name__}' is missing a '__doc_py_example__'."
            )

        md = "#### Examples\n\n"
        md += "<Tabs>\n"
        if yaml_example:
            # Validate the YAML example's syntax.
            try:
                yaml.safe_load(yaml_example)
            except Exception as e:  # noqa: BLE001
                raise ValueError(
                    f"'{t.__name__}.__doc_yaml_example__' is not valid YAML syntax"
                ) from e

            yaml_example = yaml_example.strip("\n")
            md += '<TabItem value="yamlconfig" label="YAML">\n'
            md += f"```yaml\n{yaml_example}\n```\n"
            md += "</TabItem>\n"
        if py_example:
            # Validate the Python example's syntax.
            try:
                ast.parse(py_example)
            except Exception as e:  # noqa: BLE001
                raise ValueError(
                    f"'{t.__name__}.__doc_py_example__' is not valid Python syntax"
                ) from e

            py_example = py_example.strip("\n")
            md += '<TabItem value="pythonsdk" label="Python">\n'
            md += f"```python\n{py_example}\n```\n"
            md += "</TabItem>\n"
        if cli_example:
            cli_example = cli_example.strip("\n")
            md += '<TabItem value="cli" label="CLI">\n'
            md += f"```bash\n{cli_example}\n```\n"
            md += "</TabItem>\n"

        md += "</Tabs>\n"

        return md

    def _gen_markdown_for_model(self, t: ModelType) -> str:
        """Generate a section for a model type (config/status, or enum).

        For config/status types, the sections will be:
            - Fields (all fields must be documented via docstring metadata).
            - Methods (standard methods shared across model types).
            - Examples (every model must contain examples using the magic attributes).

        For enums, the sections will be:
            - Values (all values must be documented using the __docstrings__ attribute).
        """
        assert isinstance(t, (ModelBaseType, ModelEnumType))

        md = f"### `{t.__name__}`"
        assert isinstance(t.__doc__, str)
        md += "\n\n" + t.__doc__ + "\n\n"

        if isinstance(t, ModelBaseType):
            md += "#### Fields\n\n"
            for field in fields(t):
                if field.name.startswith("_"):
                    # Skip private fields.
                    continue

                docstring = field.metadata.get("docstring", None)
                if not docstring:
                    raise ValueError(
                        f"Model '{t.__name__}' is missing a docstring for field '{field.name}'"
                    )

                md += f"- **`{field.name}` ({self._model_type_to_string(field.type)})**: {docstring}\n"

                customer_hosted_only = field.metadata.get("customer_hosted_only", False)
                if customer_hosted_only:
                    md += f"  - {CUSTOMER_HOSTED_QUALIFIER}\n"
            md += "\n\n"

            md += "#### Python Methods\n\n"
            md += "```python\n"
            if t.__name__.endswith("Config"):
                # Only include constructor docs for config models.
                md += f"def __init__(self, **fields) -> {t.__name__}\n"
                md += '    """Construct a model with the provided field values set."""\n\n'
                md += f"def options(self, **fields) -> {t.__name__}\n"
                md += '    """Return a copy of the model with the provided field values overwritten."""\n\n'
            md += "def to_dict(self) -> Dict[str, Any]\n"
            md += '    """Return a dictionary representation of the model."""\n'
            md += "```\n"

            md += self._gen_example_tabs(t)
        elif isinstance(t, ModelEnumType):
            md += "#### Values\n\n"
            for value in t.__members__:
                if not str(value).startswith("_"):
                    docstring = t.__docstrings__[value]
                    md += f" - **`{value}`**: {docstring}\n"
            md += "\n"

        return md

    def _gen_markdown_for_cli_command(
        self, c: click.Command, *, cli_prefix: str
    ) -> str:
        """Generate a markdown section for a CLI command.

        The sections will be:
            - Usage (signature + help str)
            - Options (documentation is pulled from the help strings)

        TODO(edoakes): add examples for CLI command usage.
        """
        ctx = click.Context(command=c)
        usage_str = " ".join(c.collect_usage_pieces(ctx))
        info_dict: Dict[str, Any] = c.to_info_dict(ctx)

        md = f"### `{cli_prefix} {c.name}`\n\n"
        md += "**Usage**\n\n"
        md += f"`{cli_prefix} {c.name} {usage_str}`\n\n"
        md += info_dict["help"] + "\n\n"

        options = [
            param
            for param in info_dict["params"]
            if param["param_type_name"] == "option"
        ]
        if options:
            md += "**Options**\n\n"
            for param in options:
                if param["name"] in CLI_OPTIONS_TO_SKIP:
                    continue

                name = "/".join(param["opts"])
                help_str = param.get("help", None)
                assert (
                    help_str
                ), f"Missing help string for option '{name}' in command '{c.name}'"
                md += f"- **`{name}`**: {help_str}\n"
            md += "\n"

        return md

    def _gen_markdown_for_sdk_command(self, c: Callable, *, sdk_prefix: str) -> str:
        """Generate a markdown section for an SDK command.

        The sections will be:
            - Arguments (docstrings pulled from __arg_docstrings__ magic attribute)
            - Returns (if the return type annotation is not None)
        """
        md = f"### `{sdk_prefix}.{c.__name__}`\n\n"

        if not c.__doc__:
            raise ValueError(
                f"SDK command '{sdk_prefix}.{c.__name__}' is missing a docstring."
            )

        md += c.__doc__ + "\n"

        signature = inspect.signature(c)
        if len(signature.parameters) > 0:
            # TODO: add (optional) tag or `= None`.
            md += "\n**Arguments**\n\n"
            for name, param in signature.parameters.items():
                # Skip private arguments.
                if name.startswith("_"):
                    continue

                assert param.annotation is not inspect.Parameter.empty
                type_str = "(" + self._model_type_to_string(param.annotation) + ")"
                if param.default != inspect.Parameter.empty:
                    type_str += f" = {param.default!s}"

                arg_docs = c.__arg_docstrings__.get(name, None)  # type: ignore
                if not arg_docs:
                    raise ValueError(
                        f"SDK command '{sdk_prefix}.{c.__name__}' is missing a docstring for argument '{name}'"
                    )

                md += f"- **`{name}` {type_str}**: {arg_docs}"
                md += "\n"
            md += "\n"

        if signature.return_annotation != inspect.Signature.empty:
            return_str = self._model_type_to_string(signature.return_annotation)
            md += f"**Returns**: {return_str}\n\n"

        md += self._gen_example_tabs(c)

        return md
