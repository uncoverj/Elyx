import asyncio

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_database_url, get_settings
from app.database import Base, engine, get_db
from app.deps import get_current_user
from app.models import ExternalAccount, Game, LeaderboardEntry, Letter, Like, Match, Profile, Skip, Stats, TrustVote, User
from app.rate_limit import enforce_daily_limit
from app.schemas import ActionTarget, LetterIn, LinkAccountIn, MatchOut, ProfileIn, TrustVoteIn
from app.services.background_refresh import background_refresh_loop, can_manual_refresh
from app.services.leaderboard import get_leaderboard, get_user_position, rebuild_all_leaderboards
from app.services.matching import next_candidate
from app.services.stats_refresh import refresh_user_stats
from app.services.trust import check_suspicion, check_vote_cooldown, compute_weighted_trust
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


_background_tasks: list[asyncio.Task] = []


@app.on_event("startup")
async def seed_games() -> None:
    if get_database_url().startswith("sqlite"):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    from app.database import SessionLocal

    async with SessionLocal() as session:
        exists = (await session.execute(select(Game.id).limit(1))).scalar_one_or_none()
        if not exists:
            session.add_all(
                [
                    Game(name="Valorant"),
                    Game(name="CS2"),
                    Game(name="Dota 2"),
                    Game(name="League of Legends"),
                    Game(name="Apex Legends"),
                    Game(name="Overwatch 2"),
                    Game(name="Fortnite"),
                    Game(name="Other"),
                ]
            )
            await session.commit()

    # Start background stats refresh loop (every 30 min)
    task = asyncio.create_task(background_refresh_loop(SessionLocal, interval_minutes=30))
    _background_tasks.append(task)


@app.on_event("shutdown")
async def cancel_background_tasks() -> None:
    for task in _background_tasks:
        task.cancel()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/test-keys")
async def test_api_keys():
    """Test all configured API keys and return their validity status."""
    import httpx

    results = {}

    # Test Faceit
    faceit_key = settings.faceit_api_key
    if faceit_key:
        try:
            async with httpx.AsyncClient(timeout=8.0) as c:
                r = await c.get(
                    "https://open.faceit.com/data/v4/players",
                    params={"nickname": "s1mple"},
                    headers={"Authorization": f"Bearer {faceit_key}"},
                )
                # 200 = found, 404 = player not found (key valid!), 401/400 = bad key
                ok = r.status_code in (200, 404, 403)
                results["faceit"] = {"status": "ok" if ok else "invalid", "code": r.status_code}
        except Exception as e:
            results["faceit"] = {"status": "error", "detail": str(e)}
    else:
        results["faceit"] = {"status": "not_set"}

    # Test Riot
    riot_key = settings.riot_api_key
    if riot_key:
        try:
            async with httpx.AsyncClient(timeout=8.0) as c:
                r = await c.get(
                    "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Faker/T1",
                    headers={"X-Riot-Token": riot_key},
                )
                results["riot"] = {"status": "ok" if r.status_code == 200 else "expired" if r.status_code == 401 else "error", "code": r.status_code}
        except Exception as e:
            results["riot"] = {"status": "error", "detail": str(e)}
    else:
        results["riot"] = {"status": "not_set"}

    # Test Henrik (Valorant)
    henrik_key = settings.henrik_api_key
    try:
        async with httpx.AsyncClient(timeout=8.0) as c:
            headers = {}
            if henrik_key:
                headers["Authorization"] = henrik_key
            r = await c.get("https://api.henrikdev.xyz/valorant/v1/account/TenZ/0505", headers=headers)
            # 200 = found, 404 = not found (key valid!), 401 = auth required
            ok = r.status_code in (200, 404, 403)
            results["henrik"] = {"status": "ok" if ok else "auth_required" if r.status_code == 401 else "error", "code": r.status_code}
    except Exception as e:
        results["henrik"] = {"status": "error", "detail": str(e)}

    return {
        "keys": results,
        "instructions": {
            "faceit": "Get key at https://developers.faceit.com/ → Create App → Server-side API key",
            "riot": "Get key at https://developer.riotgames.com/ → Dev key expires every 24h. For permanent: register a production app",
            "henrik": "Get key at https://docs.henrikdev.xyz/ → Register → API key (free tier available)",
        },
    }


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

    # Cooldown check
    allowed, remaining = await check_vote_cooldown(db, current_user.id, target_user_id)
    if not allowed:
        raise HTTPException(status_code=429, detail=f"Vote cooldown: {remaining // 60} min remaining")

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

    # Suspicion check on target after downvote
    suspicious = False
    if value == -1:
        suspicious = await check_suspicion(db, target_user_id)

    return {"ok": True, "suspicious_activity": suspicious}


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


@app.post("/account/link/blizzard")
async def link_blizzard(
    payload: LinkAccountIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _link_account(db, current_user.id, "blizzard", payload.account_ref)


@app.post("/account/link/epic")
async def link_epic(
    payload: LinkAccountIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _link_account(db, current_user.id, "epic", payload.account_ref)


@app.post("/account/link/faceit")
async def link_faceit(
    payload: LinkAccountIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _link_account(db, current_user.id, "faceit", payload.account_ref)


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
    stats = (await db.execute(select(Stats).where(Stats.user_id == current_user.id))).scalar_one_or_none()
    allowed, wait_seconds = can_manual_refresh(current_user, stats)
    if not allowed:
        minutes = wait_seconds // 60
        raise HTTPException(
            status_code=429,
            detail=f"Refresh cooldown: try again in {minutes} min",
        )
    result = await refresh_user_stats(db, current_user.id)

    # Rebuild leaderboard for user's game after refresh
    if result.get("ok"):
        profile = (await db.execute(select(Profile).where(Profile.user_id == current_user.id))).scalar_one_or_none()
        if profile:
            from app.services.leaderboard import rebuild_leaderboard
            await rebuild_leaderboard(db, profile.game_id)

    return result


# ===== Leaderboard =====

@app.get("/leaderboard/{game_id}")
async def leaderboard(
    game_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get leaderboard for a game with pagination."""
    game = (await db.execute(select(Game).where(Game.id == game_id))).scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    entries = await get_leaderboard(db, game_id, offset=offset, limit=limit)

    # Total count for pagination
    total = (
        await db.execute(
            select(LeaderboardEntry.id).where(LeaderboardEntry.game_id == game_id)
        )
    ).all()

    return {
        "game": game.name,
        "total": len(total),
        "offset": offset,
        "limit": limit,
        "entries": entries,
    }


@app.get("/leaderboard/{game_id}/me")
async def leaderboard_me(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's position on a game leaderboard."""
    position = await get_user_position(db, game_id, current_user.id)
    if not position:
        return {"position": None, "message": "Not ranked yet"}
    return position


@app.post("/leaderboard/rebuild")
async def leaderboard_rebuild(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Admin/service endpoint to rebuild all leaderboards."""
    results = await rebuild_all_leaderboards(db)
    return {"ok": True, "rebuilt": results}


# ===== Premium =====

@app.get("/premium/status")
async def premium_status(current_user: User = Depends(get_current_user)):
    from datetime import datetime, timezone
    is_active = current_user.is_premium
    days_left = 0
    if current_user.premium_until:
        delta = current_user.premium_until - datetime.now(timezone.utc)
        days_left = max(0, delta.days)
        if days_left == 0:
            is_active = False
    return {
        "is_premium": is_active,
        "premium_until": current_user.premium_until.isoformat() if current_user.premium_until else None,
        "days_left": days_left,
        "features": {
            "daily_likes": "unlimited" if is_active else 100,
            "daily_letters": "unlimited" if is_active else 5,
            "priority_search": is_active,
            "profile_badge": is_active,
            "see_who_liked": is_active,
        },
    }


@app.post("/premium/activate")
async def premium_activate(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    if current_user.premium_until and current_user.premium_until > now:
        current_user.premium_until = current_user.premium_until + timedelta(days=30)
    else:
        current_user.premium_until = now + timedelta(days=30)
    current_user.is_premium = True
    await db.commit()
    return {"ok": True, "premium_until": current_user.premium_until.isoformat()}
