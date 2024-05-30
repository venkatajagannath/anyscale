from typing import Dict, Tuple

import click


# Take from https://stackoverflow.com/questions/51846634/click-dynamic-defaults-for-prompts-based-on-other-options
class OptionPromptNull(click.Option):
    """
    Option class that allows default values based on previous params
    """

    _value_key = "_default_val"

    def __init__(self, *args, **kwargs):
        self.default_option = kwargs.pop("default_option", None)
        super().__init__(*args, **kwargs)

    def get_default(self, ctx, **kwargs):
        if not hasattr(self, self._value_key):
            if self.default_option is None:
                default = super().get_default(ctx, **kwargs)
            else:
                arg = ctx.params.get(self.default_option)
                if arg is not None:
                    default = self.type_cast_value(ctx, self.default(arg))
                else:
                    default = None
            setattr(self, self._value_key, default)
        return getattr(self, self._value_key)


# Taken from https://stackoverflow.com/questions/44247099/click-command-line-interfaces-make-options-required-if-other-optional-option-is
class NotRequiredIf(click.Option):
    """
    Option class that allows an option to be not required if a separate option is available.
    """

    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop("not_required_if")
        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs["help"] = (
            kwargs.get("help", "")
            + " NOTE: This argument is mutually exclusive with %s"
            % self.not_required_if
        ).strip()
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts
        other_present = self.not_required_if in opts

        if other_present:
            if we_are_present:
                raise click.UsageError(
                    "Illegal usage: `%s` is mutually exclusive with `%s`"
                    % (self.name, self.not_required_if)
                )
            else:
                self.prompt = None
                self.default = None

        return super().handle_parse_result(ctx, opts, args)


def convert_kv_strings_to_dict(strings: Tuple[str]) -> Dict[str, str]:
    """Convert args/env_vars of the form "key=val" into a dictionary of {key: val}.

    NOTE(edoakes): this mimics the functionality of the `serve run` CLI and should be
    kept in sync with it.
    """
    ret_dict = {}
    for s in strings:
        split = s.split("=")
        if len(split) != 2:
            raise click.ClickException(
                f"Invalid key-value string '{s}'. Must be of the form 'key=value'."
            )

        ret_dict[split[0]] = split[1]

    return ret_dict
