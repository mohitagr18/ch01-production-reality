"""
Proves the model name is read from GEMINI_MODEL at call time (not
hardcoded), and falls back to the documented default when unset.
"""
from src.services import llm_client


def test_default_model_used_when_env_var_unset(monkeypatch):
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    assert llm_client._get_model_name() == llm_client.DEFAULT_MODEL_NAME


def test_env_var_overrides_default_model(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "gemini-1.5-pro")
    assert llm_client._get_model_name() == "gemini-1.5-pro"
