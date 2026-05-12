from config import get_settings


def test_get_settings_reads_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-test-key")
    monkeypatch.setenv("TMDB_API_KEY", "tmdb-test-key")
    s = get_settings()
    assert s.gemini_key == "gemini-test-key"
    assert s.tmdb_key == "tmdb-test-key"


def test_get_settings_missing_keys_returns_empty_strings(monkeypatch, tmp_path):
    # Run config from an empty cwd so .env is not picked up
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("TMDB_API_KEY", raising=False)
    s = get_settings()
    assert s.gemini_key == ""
    assert s.tmdb_key == ""
