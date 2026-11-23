from agentsbuilder.config import Settings


def test_settings_read_from_environment(monkeypatch):
    monkeypatch.setenv("AGENTSBUILDER_CHAT_MODEL", "test-model")
    monkeypatch.setenv("AGENTSBUILDER_DEFAULT_TENANT_ID", "acme")
    settings = Settings(_env_file=None)
    assert settings.chat_model == "test-model"
    assert settings.default_tenant_id == "acme"


def test_api_key_is_not_exposed_in_repr():
    settings = Settings(_env_file=None, llm_api_key="secret-value")
    assert "secret-value" not in repr(settings)
