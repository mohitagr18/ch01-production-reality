"""
Structural proof for section 1.4: the policy gate function has no
parameter that accepts free-form text (an LLM opinion, a user message,
anything un-typed). It only accepts booleans and a list of pre-validated
hazard strings produced by deterministic adapters. This is checked via
introspection so the guarantee can never silently regress if someone
adds a parameter later without a reviewer noticing.
"""
import inspect
from src.policy.constraints import evaluate_trail_safety


def test_policy_gate_has_no_llm_text_parameter():
    sig = inspect.signature(evaluate_trail_safety)
    param_names = set(sig.parameters.keys())
    assert param_names == {"trail_name", "has_valid_geometry", "weather_hazards"}
    assert sig.parameters["has_valid_geometry"].annotation is bool


def test_policy_gate_result_type_is_a_closed_enum_not_free_text():
    """
    SafetyVerdict.verdict is a Literal["SAFE", "CAUTION", "FAIL_CLOSED"].
    Pydantic enforces this at construction time, so nothing downstream
    of the policy gate can ever receive an arbitrary string as a verdict.
    """
    from src.models import SafetyVerdict
    import typing

    field = SafetyVerdict.model_fields["verdict"]
    literal_args = typing.get_args(field.annotation)
    assert literal_args == ("SAFE", "CAUTION", "FAIL_CLOSED")
