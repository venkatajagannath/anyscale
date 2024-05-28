from dataclasses import dataclass, field
import re
from typing import Dict, Optional, Union

import pytest

from anyscale._private.models import ModelBase, ModelEnum


def test_invalid_subclass():
    """Validate that the subclass is a dataclass with frozen=True."""

    class NotADataclass(ModelBase):
        pass

    with pytest.raises(
        TypeError,
        match="Subclasses of `ModelBase` must be dataclasses with `frozen=True`.",
    ):
        NotADataclass()

    @dataclass
    class NotFrozen(ModelBase):
        pass

    with pytest.raises(
        TypeError,
        match="Subclasses of `ModelBase` must be dataclasses with `frozen=True`.",
    ):
        NotFrozen()


class TestValidatorValidation:
    def test_missing(self):
        @dataclass(frozen=True)
        class Subclass(ModelBase):
            some_field: str = field(metadata={"docstring": "test"})
            some_other_field: str = field(metadata={"docstring": "test"})

            def _validate_some_field(self, some_field: str):
                pass

        with pytest.raises(
            RuntimeError,
            match="Model 'Subclass' is missing validator method for field 'some_other_field'.",
        ):
            Subclass(some_field="hi", some_other_field="hi2")

    def test_multiple_params(self):
        @dataclass(frozen=True)
        class Subclass(ModelBase):
            some_field: str = field(metadata={"docstring": "test"})

            def _validate_some_field(self, some_field: str, something_else: int):
                pass

        with pytest.raises(
            TypeError,
            match=re.escape(
                "Validator for field 'some_field' must take the field value as its only argument."
            ),
        ):
            Subclass(some_field="hi")

    def test_wrong_param_name(self):
        @dataclass(frozen=True)
        class Subclass(ModelBase):
            some_field: str = field(metadata={"docstring": "test"})

            def _validate_some_field(self, arg: str):
                pass

        with pytest.raises(
            TypeError,
            match=re.escape(
                "Validator for field 'some_field' has invalid parameter name (must match the field name)."
            ),
        ):
            Subclass(some_field="hi")

    def test_missing_param_annotation(self):
        @dataclass(frozen=True)
        class Subclass(ModelBase):
            some_field: str = field(metadata={"docstring": "test"})

            def _validate_some_field(self, some_field):
                pass

        with pytest.raises(
            TypeError,
            match=re.escape(
                "Validator for field 'some_field' is missing a type annotation"
            ),
        ):
            Subclass(some_field="hi")

    def test_wrong_param_annotation(self):
        @dataclass(frozen=True)
        class Subclass(ModelBase):
            some_field: str = field(metadata={"docstring": "test"})

            def _validate_some_field(self, some_field: int):
                pass

        with pytest.raises(
            TypeError,
            match=re.escape(
                "Validator for field 'some_field' has the wrong type annotation"
            ),
        ):
            Subclass(some_field="hi")


def test_validators():
    @dataclass(frozen=True)
    class Subclass(ModelBase):
        some_field: str = field(metadata={"docstring": "test"})
        some_other_field: str = field(metadata={"docstring": "test"})

        def _validate_some_field(self, some_field: str):
            if not isinstance(some_field, str):
                raise TypeError("'some_field' must be a string.")

        def _validate_some_other_field(self, some_other_field: str):
            if not isinstance(some_other_field, str):
                raise TypeError("'some_other_field' must be a string.")

    Subclass(some_field="hi", some_other_field="hi2")
    with pytest.raises(TypeError, match="'some_other_field' must be a string."):
        Subclass(some_field="hi", some_other_field=123)


def test_update_value_from_validator():
    @dataclass(frozen=True)
    class Subclass(ModelBase):
        some_field: str = field(metadata={"docstring": "test"})

        def _validate_some_field(self, some_field: str) -> str:
            if not isinstance(some_field, str):
                raise TypeError("'some_field' must be a string.")

            return some_field + "-updated"

    assert Subclass(some_field="hi").some_field == "hi-updated"


class TestToDict:
    def test_exclude_none(self):
        @dataclass(frozen=True)
        class SubModel(ModelBase):
            sub_field_1: Optional[str] = field(
                metadata={"detailed": True, "docstring": "test"}
            )
            sub_field_2: Optional[str] = field(metadata={"docstring": "test"})

            def _validate_sub_field_1(self, sub_field_1: Optional[str]):
                pass

            def _validate_sub_field_2(self, sub_field_2: Optional[str]):
                pass

        @dataclass(frozen=True)
        class Model(ModelBase):
            sub_model: Optional[SubModel] = field(metadata={"docstring": "test"})

            def _validate_sub_model(self, sub_model: Optional[SubModel]):
                pass

        assert Model(sub_model=None).to_dict() == {}
        assert Model(sub_model=None).to_dict(exclude_none=False) == {"sub_model": None}
        assert Model(
            sub_model=SubModel(sub_field_1=None, sub_field_2="hi")
        ).to_dict() == {"sub_model": {"sub_field_2": "hi"},}
        assert Model(sub_model=SubModel(sub_field_1=None, sub_field_2="hi")).to_dict(
            exclude_none=False
        ) == {"sub_model": {"sub_field_1": None, "sub_field_2": "hi"},}


class TestFromDict:
    def test_basic(self):
        @dataclass(frozen=True)
        class Model(ModelBase):
            field_1: str = field(metadata={"docstring": "test"})
            field_2: Optional[int] = field(default=None, metadata={"docstring": "test"})

            def _validate_field_1(self, field_1: str):
                pass

            def _validate_field_2(self, field_2: Optional[int]):
                pass

        assert Model.from_dict({"field_1": "hi"},) == Model(field_1="hi")

        assert Model.from_dict({"field_1": "hi", "field_2": 1},) == Model(
            field_1="hi", field_2=1
        )

        with pytest.raises(
            TypeError, match="missing 1 required positional argument: 'field_1'"
        ):
            Model.from_dict({"field_2": 1},)

    def test_nested(self):
        @dataclass(frozen=True)
        class SubModel(ModelBase):
            sub_field: int = field(metadata={"docstring": "test"})

            def _validate_sub_field(self, sub_field: int):
                pass

        @dataclass(frozen=True)
        class Model(ModelBase):
            field_1: str = field(metadata={"docstring": "test"})
            sub_model: Union[Dict, SubModel] = field(metadata={"docstring": "test"})
            optional_sub_model: Union[None, Dict, SubModel] = field(
                default=None, metadata={"docstring": "test"}
            )

            def _validate_field_1(self, field_1: str):
                pass

            def _validate_sub_model(self, sub_model: Union[Dict, SubModel]) -> SubModel:
                if isinstance(sub_model, dict):
                    sub_model = SubModel.from_dict(sub_model)

                if not isinstance(sub_model, SubModel):
                    raise TypeError("'sub_model' must be SubModel or dict")

                return sub_model

            def _validate_optional_sub_model(
                self, optional_sub_model: Union[None, Dict, SubModel]
            ) -> Optional[SubModel]:
                if optional_sub_model is None:
                    return optional_sub_model

                if isinstance(optional_sub_model, dict):
                    optional_sub_model = SubModel.from_dict(optional_sub_model)

                if not isinstance(optional_sub_model, SubModel):
                    raise TypeError("'optional_sub_model' must be SubModel or dict")

                return optional_sub_model

        assert Model.from_dict(
            {"field_1": "hi", "sub_model": {"sub_field": 1}},
        ) == Model(field_1="hi", sub_model=SubModel(sub_field=1))

        assert Model.from_dict(
            {"field_1": "hi", "sub_model": SubModel(sub_field=1)},
        ) == Model(field_1="hi", sub_model=SubModel(sub_field=1))

        assert Model.from_dict(
            {
                "field_1": "hi",
                "sub_model": SubModel(sub_field=1),
                "optional_sub_model": SubModel(sub_field=1),
            },
        ) == Model(
            field_1="hi",
            sub_model=SubModel(sub_field=1),
            optional_sub_model=SubModel(sub_field=1),
        )

        assert Model.from_dict(
            {
                "field_1": "hi",
                "sub_model": SubModel(sub_field=1),
                "optional_sub_model": {"sub_field": 1},
            },
        ) == Model(
            field_1="hi",
            sub_model=SubModel(sub_field=1),
            optional_sub_model=SubModel(sub_field=1),
        )


def test_options():
    @dataclass(frozen=True)
    class Model(ModelBase):
        field_1: Optional[str] = field(metadata={"docstring": "test"})
        field_2: Optional[str] = field(metadata={"docstring": "test"})

        def _validate_field_1(self, field_1: Optional[str]):
            pass

        def _validate_field_2(self, field_2: Optional[str]):
            pass

    m0 = Model(field_1=None, field_2="hi2")
    assert m0.field_1 is None
    assert m0.field_2 == "hi2"

    # Check that only the passed value is overwritten.
    # m0 should be unmodified.
    m1 = m0.options(field_1="hi1")
    assert m1.field_1 == "hi1"
    assert m1.field_2 == "hi2"
    assert m0.field_1 is None
    assert m0.field_2 == "hi2"

    # Check that `None` can be passed to overwrite a value.
    m2 = m0.options(field_2=None)
    assert m2.field_1 is None
    assert m2.field_2 is None
    assert m0.field_1 is None
    assert m0.field_2 == "hi2"

    # Test passing an unknown field.
    with pytest.raises(
        ValueError,
        match=re.escape("Unexpected values passed to '.options': ['unknown']."),
    ):
        m0.options(unknown="oops")


class TestModelEnum:
    def test_missing_docstrings_value(self):
        with pytest.raises(
            ValueError,
            match=re.escape(
                "ModelEnum 'CustomEnum.__docstrings__' is missing docstrings for values: ['VAL']"
            ),
        ):

            class CustomEnum(ModelEnum):
                VAL = "VAL"

    def test_bad_docstrings_type(self):
        with pytest.raises(
            TypeError,
            match=re.escape("ModelEnum 'CustomEnum.__docstrings__' is the wrong type"),
        ):

            class CustomEnum(ModelEnum):
                VAL = "VAL"

                __docstrings__ = {VAL: 123}

    def test_convert_to_str(self):
        class CustomEnum(ModelEnum):
            VAL = "VAL"

            __docstrings__ = {VAL: "test"}

        @dataclass(frozen=True)
        class Model(ModelBase):
            e: CustomEnum = field(metadata={"docstring": "test"})

            def _validate_e(self, e: CustomEnum):
                pass

        assert Model(e=CustomEnum.VAL).to_dict() == {"e": "VAL"}
