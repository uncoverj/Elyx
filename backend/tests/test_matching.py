from app.services.matching import rank_similarity, tag_overlap


def test_rank_similarity_close_ranks() -> None:
    assert rank_similarity("gold", "platinum") > 0.7


def test_rank_similarity_far_ranks() -> None:
    assert rank_similarity("iron", "radiant") == 0.0


def test_rank_similarity_missing_rank() -> None:
    assert rank_similarity(None, "gold") == 0.25


def test_tag_overlap() -> None:
    score = tag_overlap(["duo", "calm", "competitive"], ["calm", "fun", "duo"])
    assert round(score, 2) == 0.67
