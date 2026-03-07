from datetime import datetime

from pydantic import BaseModel, Field


class ProfileIn(BaseModel):
    nickname: str = Field(min_length=2, max_length=64)
    gender: str
    age: int = Field(ge=13, le=99)
    game_id: int
    bio: str = Field(min_length=10, max_length=400)
    media_type: str
    media_file_id: str
    roles: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    green_flags: list[str] = Field(default_factory=list, max_length=3)
    dealbreaker: str | None = None
    mood_status: str | None = None


class StatsIn(BaseModel):
    kd: float | None = None
    winrate: float | None = None
    rank_name: str | None = None
    rank_points: int | None = None
    unified_score: int = 0
    source: str = "manual"
    source_status: str = "ok"
    verified: bool = False
    updated_at: datetime | None = None


class ProfileOut(BaseModel):
    user_id: int
    tg_id: int
    username: str | None
    nickname: str
    gender: str
    age: int
    game_id: int
    game_name: str
    bio: str
    media_type: str
    media_file_id: str
    roles: list[str]
    tags: list[str]
    green_flags: list[str] = []
    dealbreaker: str | None = None
    mood_status: str | None = None
    trust_up: int
    trust_down: int
    trust_score: float
    is_premium: bool = False
    stats: StatsIn | None = None


class ActionTarget(BaseModel):
    target_user_id: int


class LetterIn(ActionTarget):
    text: str = Field(min_length=1, max_length=500)


class ReportIn(ActionTarget):
    reason: str = Field(min_length=5, max_length=500)


class MatchOut(BaseModel):
    match_id: int
    user_id: int
    nickname: str
    username: str | None
    game_name: str
    created_at: datetime


class LinkAccountIn(BaseModel):
    account_ref: str = Field(min_length=2, max_length=128)


class TrustVoteIn(ActionTarget):
    value: int


class SearchCandidate(BaseModel):
    user_id: int
    score: float
    profile: ProfileOut
