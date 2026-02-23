from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_database_url, get_settings
from app.database import Base, engine, get_db
from app.deps import get_current_user
from app.models import ExternalAccount, Game, Letter, Like, Match, Profile, Skip, Stats, TrustVote, User
from app.rate_limit import enforce_daily_limit
from app.schemas import ActionTarget, LetterIn, LinkAccountIn, MatchOut, ProfileIn, TrustVoteIn
from app.services.matching import next_candidate
from app.utils import build_profile_out

settings = get_settings()
app = FastAPI(title="Elyx API", version="0.1.0")

origins = [x.strip() for x in settings.cors_origin.split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def seed_games() -> None:
    if get_database_url().startswith("sqlite"):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    from app.database import SessionLocal

    async with SessionLocal() as session:
        exists = (await session.execute(select(Game.id).limit(1))).scalar_one_or_none()
        if exists:
            return
        session.add_all(
            [
                Game(name="Valorant"),
                Game(name="CS2"),
                Game(name="Dota 2"),
                Game(name="League of Legends"),
                Game(name="Apex Legends"),
                Game(name="Other"),
            ]
        )
        await session.commit()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/games")
async def list_games(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _ = current_user
    rows = (await db.execute(select(Game).where(Game.is_active.is_(True)).order_by(Game.name.asc()))).scalars().all()
    return [{"id": g.id, "name": g.name} for g in rows]


@app.get("/profiles/me")
async def get_my_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    profile = await build_profile_out(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@app.put("/profiles/me")
async def upsert_my_profile(
    payload: ProfileIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    game_exists = (await db.execute(select(Game.id).where(Game.id == payload.game_id))).scalar_one_or_none()
    if not game_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid game")

    profile = (await db.execute(select(Profile).where(Profile.user_id == current_user.id))).scalar_one_or_none()
    if not profile:
        profile = Profile(user_id=current_user.id, **payload.model_dump())
        db.add(profile)
    else:
        for key, value in payload.model_dump().items():
            setattr(profile, key, value)

    await db.commit()
    return await build_profile_out(db, current_user.id)


@app.get("/profiles/{user_id}")
async def get_profile(user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _ = current_user
    profile = await build_profile_out(db, user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@app.get("/search/next")
async def search_next(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    candidate = await next_candidate(db, current_user.id)
    if not candidate:
        return {"candidate": None}
    card = await build_profile_out(db, candidate.user_id)
    return {"candidate": card}


@app.post("/actions/like")
async def action_like(
    payload: ActionTarget,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot like self")

    if not current_user.is_premium:
        await enforce_daily_limit(current_user.id, "likes", 100)

    existing = (
        await db.execute(
            select(Like).where(
                and_(Like.from_user_id == current_user.id, Like.to_user_id == payload.target_user_id)
            )
        )
    ).scalar_one_or_none()
    if not existing:
        db.add(Like(from_user_id=current_user.id, to_user_id=payload.target_user_id))

    reciprocal = (
        await db.execute(
            select(Like).where(
                and_(Like.from_user_id == payload.target_user_id, Like.to_user_id == current_user.id)
            )
        )
    ).scalar_one_or_none()

    match_created = False
    if reciprocal:
        a, b = sorted((current_user.id, payload.target_user_id))
        existing_match = (
            await db.execute(select(Match).where(and_(Match.user_a == a, Match.user_b == b)))
        ).scalar_one_or_none()
        if not existing_match:
            db.add(Match(user_a=a, user_b=b))
            match_created = True

    await db.commit()
    return {"ok": True, "match_created": match_created}


@app.post("/actions/skip")
async def action_skip(
    payload: ActionTarget,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot skip self")

    existing = (
        await db.execute(
            select(Skip).where(
                and_(Skip.from_user_id == current_user.id, Skip.to_user_id == payload.target_user_id)
            )
        )
    ).scalar_one_or_none()
    if not existing:
        db.add(Skip(from_user_id=current_user.id, to_user_id=payload.target_user_id))
        await db.commit()
    return {"ok": True}


@app.post("/actions/letter")
async def action_letter(
    payload: LetterIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send letter to self")

    if not current_user.is_premium:
        await enforce_daily_limit(current_user.id, "letters", 5)

    db.add(Letter(from_user_id=current_user.id, to_user_id=payload.target_user_id, text=payload.text))
    await db.commit()
    return {"ok": True}


@app.get("/matches")
async def get_matches(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(Match).where(or_(Match.user_a == current_user.id, Match.user_b == current_user.id)).order_by(Match.created_at.desc())
        )
    ).scalars().all()

    output: list[MatchOut] = []
    for row in rows:
        other_id = row.user_b if row.user_a == current_user.id else row.user_a
        profile = (await db.execute(select(Profile).where(Profile.user_id == other_id))).scalar_one_or_none()
        if not profile:
            continue
        user = (await db.execute(select(User).where(User.id == other_id))).scalar_one()
        game = (await db.execute(select(Game).where(Game.id == profile.game_id))).scalar_one()
        output.append(
            MatchOut(
                match_id=row.id,
                user_id=other_id,
                nickname=profile.nickname,
                username=user.username,
                game_name=game.name,
                created_at=row.created_at,
            )
        )

    return output


@app.get("/matches/{match_id}")
async def get_match_details(match_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    row = (await db.execute(select(Match).where(Match.id == match_id))).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Match not found")
    if current_user.id not in (row.user_a, row.user_b):
        raise HTTPException(status_code=403, detail="Forbidden")

    other_id = row.user_b if row.user_a == current_user.id else row.user_a
    profile = await build_profile_out(db, other_id)
    return {"match_id": row.id, "profile": profile}


@app.post("/trust/upvote")
async def trust_upvote(
    payload: ActionTarget,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _trust_vote(payload.target_user_id, current_user, db, 1)


@app.post("/trust/downvote")
async def trust_downvote(
    payload: ActionTarget,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _trust_vote(payload.target_user_id, current_user, db, -1)


async def _trust_vote(target_user_id: int, current_user: User, db: AsyncSession, value: int):
    if target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot vote self")

    is_matched = (
        await db.execute(
            select(Match).where(
                or_(
                    and_(Match.user_a == current_user.id, Match.user_b == target_user_id),
                    and_(Match.user_a == target_user_id, Match.user_b == current_user.id),
                )
            )
        )
    ).scalar_one_or_none()
    if not is_matched:
        raise HTTPException(status_code=400, detail="Trust vote allowed only after match")

    existing = (
        await db.execute(
            select(TrustVote).where(
                and_(TrustVote.from_user_id == current_user.id, TrustVote.to_user_id == target_user_id)
            )
        )
    ).scalar_one_or_none()
    if existing:
        existing.value = value
    else:
        db.add(TrustVote(from_user_id=current_user.id, to_user_id=target_user_id, value=value))
    await db.commit()
    return {"ok": True}


@app.post("/account/link/riot")
async def link_riot(
    payload: LinkAccountIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _link_account(db, current_user.id, "riot", payload.account_ref)


@app.post("/account/link/steam")
async def link_steam(
    payload: LinkAccountIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _link_account(db, current_user.id, "steam", payload.account_ref)


async def _link_account(db: AsyncSession, user_id: int, provider: str, account_ref: str):
    row = (
        await db.execute(
            select(ExternalAccount).where(
                and_(ExternalAccount.user_id == user_id, ExternalAccount.provider == provider)
            )
        )
    ).scalar_one_or_none()
    if row:
        row.account_ref = account_ref
    else:
        db.add(ExternalAccount(user_id=user_id, provider=provider, account_ref=account_ref, verified=False))
    await db.commit()
    return {"ok": True, "provider": provider, "verified": False}


@app.post("/account/refresh-stats")
async def refresh_stats(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _ = db
    return {
        "ok": True,
        "message": "Stats refresh is stubbed. Integrate official Riot/Steam APIs for verified sync.",
        "user_id": current_user.id,
    }
