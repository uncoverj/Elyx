from app.main import SUPPORTED_ACCOUNT_PROVIDERS, SUPPORTED_GAMES
from app.services.stats_refresh import GAME_PROVIDER_MAP, PROVIDER_LABELS


def test_supported_games_are_curated() -> None:
    assert SUPPORTED_GAMES == ("Valorant", "CS2")


def test_supported_account_providers_are_curated() -> None:
    assert SUPPORTED_ACCOUNT_PROVIDERS == ("riot", "faceit")


def test_stats_refresh_provider_map_matches_supported_games() -> None:
    assert GAME_PROVIDER_MAP == {"valorant": "riot", "cs2": "faceit"}
    assert PROVIDER_LABELS["riot"].startswith("Riot ID")
    assert "FACEIT" in PROVIDER_LABELS["faceit"]
