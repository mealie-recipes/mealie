from mealie.core.config import determine_secrets

def test_determine_secret(monkeypatch):
    secret = determine_secrets()

    