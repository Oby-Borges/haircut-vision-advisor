from copy import deepcopy

import pytest

from haircut_vision.catalog import load_catalog
from haircut_vision.robot_contract import build_robot_output, validate_robot_output


def test_contract_requires_explicit_selection():
    with pytest.raises(ValueError, match="Explicit user selection"):
        build_robot_output(load_catalog()[0], user_confirmed=False)


def test_contract_is_valid_and_contains_no_actuator_fields():
    payload = build_robot_output(load_catalog()[0], user_confirmed=True)
    validate_robot_output(payload)
    assert payload["contract_type"] == "descriptive_haircut_proposal"
    forbidden = {"motor", "trajectory", "blade_state", "speed", "force", "coordinates"}
    assert forbidden.isdisjoint(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [("top_length_mm", -1), ("fade_type", "extreme"), ("user_confirmed_selection", False)],
)
def test_contract_validation_rejects_invalid_values(field, value):
    payload = build_robot_output(load_catalog()[0], user_confirmed=True)
    broken = deepcopy(payload)
    broken[field] = value
    with pytest.raises(ValueError):
        validate_robot_output(broken)
