from dataclasses import asdict, fields
from enum import Enum, EnumMeta
import inspect
from typing import Any, Dict, Iterable, Tuple, TypeVar, Union

import yaml


# In Python 3.11 there is a 'Self' introduced, but this is the
# workaround before that: https://peps.python.org/pep-0673/.
TModelBase = TypeVar("TModelBase", bound="ModelBase")


class ModelEnumType(EnumMeta):
    def __new__(cls, subcls, bases, classdict):
        cls = super().__new__(cls, subcls, bases, classdict)

        # Assert that all enum values have docstrings.
        if not isinstance(cls.__docstrings__, dict) or not all(
            isinstance(k, str) and isinstance(v, str)
            for k, v in cls.__docstrings__.items()
        ):
            raise TypeError(
                f"ModelEnum '{cls.__name__}.__docstrings__' is the wrong type. "
                "Must be a Dict[ModelEnum, str] documenting all enum values"
            )

        missing = {v.value for v in cls if not v.name.startswith("_")} - set(
            cls.__docstrings__.keys()
        )
        if missing:
            raise ValueError(
                f"ModelEnum '{cls.__name__}.__docstrings__' is missing docstrings for values: {sorted(missing)}"
            )

        return cls


class ModelEnum(str, Enum, metaclass=ModelEnumType):
    # Must be populated by subclasses to document every value.
    __docstrings__: Dict["ModelEnum", str] = {}

    def __str__(self):
        return self.name

    @classmethod
    def validate(cls, value: Union[str, "ModelEnum"]) -> "ModelEnum":
        allowed_values = [str(s) for s in cls.__members__ if not str(s).startswith("_")]
        if value.upper() in allowed_values:
            return cls(value.upper())
        else:
            raise ValueError(
                f"'{value.upper()}' is not a valid {cls.__name__}. Allowed values are {allowed_values}"
            )


class ModelBaseType(type):
    pass


class ModelBase(metaclass=ModelBaseType):
    def __new__(cls, *args, **kwargs):  # noqa: ARG003
        """Validate that the subclass is a conforming dataclass."""
        if (
            not hasattr(cls, "__dataclass_params__")
            or not cls.__dataclass_params__.frozen
        ):
            raise TypeError(
                "Subclasses of `ModelBase` must be dataclasses with `frozen=True`."
            )

        return super().__new__(cls)

    def _run_validators(self):
        """Run magic validator methods.

        Looks for methods with the name: `_validate_{field}`. The method will be called
        with the field value as its sole argument.

        If the validator has a return type annotation, the field will be updated to the
        returned value.
        """
        for field in fields(self):
            if not field.metadata.get("docstring", None):
                raise ValueError(
                    f"Model '{type(self).__name__}' is missing docstring for field '{field.name}'."
                )

            validator = getattr(self, f"_validate_{field.name}", None)
            if validator is None:
                raise RuntimeError(
                    f"Model '{type(self).__name__}' is missing validator method for field '{field.name}'."
                )

            signature: inspect.Signature = inspect.signature(validator)
            if len(signature.parameters) != 1:
                raise TypeError(
                    f"Validator for field '{field.name}' must take the field value as its only argument."
                )
            elif field.name not in signature.parameters:
                raise TypeError(
                    f"Validator for field '{field.name}' has invalid parameter name (must match the field name)."
                )
            elif signature.parameters[field.name].annotation == inspect.Parameter.empty:
                raise TypeError(
                    f"Validator for field '{field.name}' is missing a type annotation (should be '{field.type}')."
                )
            elif signature.parameters[field.name].annotation != field.type:
                raise TypeError(
                    f"Validator for field '{field.name}' has the wrong type annotation (should be '{field.type}')."
                )

            maybe_updated_field_value = validator(getattr(self, field.name))
            if signature.return_annotation != inspect.Signature.empty:
                # Only update the value if the validator has a return type annotation.
                object.__setattr__(self, field.name, maybe_updated_field_value)

    def __post_init__(self):
        self._run_validators()

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ModelBase":
        return cls(**d)

    @classmethod
    def from_yaml(cls, path: str, **kwargs) -> "ModelBase":
        with open(path) as f:
            args = yaml.safe_load(f) or {}
            if kwargs:
                args.update(kwargs)
            return cls.from_dict(args)

    def to_dict(self, *, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert the model to a dictionary representation.

        If `exclude_none` is `True`, keys whose values are `None` will be excluded.
        """

        def maybe_exclude_nones(i: Iterable[Tuple[str, Any]]):
            d = {}
            for k, v in i:
                # Exclude none values if specified.
                if exclude_none and v is None:
                    continue

                # Convert enums to their string representation.
                if isinstance(v, ModelEnum):
                    v = v.value

                d[k] = v

            return d

        return asdict(self, dict_factory=maybe_exclude_nones)

    def options(self: TModelBase, **kwargs) -> TModelBase:
        """Return a copy of the model with the provided fields updated.

        All fields in the constructor are supported. Those not provided will be unchanged.
        """
        new_instance_kwargs = {
            field.name: kwargs.pop(field.name)
            if field.name in kwargs
            else getattr(self, field.name)
            for field in fields(self)
        }
        if len(kwargs) > 0:
            raise ValueError(
                f"Unexpected values passed to '.options': {list(kwargs.keys())}."
            )

        return type(self)(**new_instance_kwargs)
