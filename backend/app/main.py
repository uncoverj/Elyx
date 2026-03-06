import asyncio
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import and_, case, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_admin_ids, get_database_url, get_settings
from app.database import Base, engine, get_db
from app.deps import get_current_user
from app.models import Block, ExternalAccount, Game, LeaderboardEntry, Letter, Like, Match, Profile, Report, Skip, Stats, TrustVote, User
from app.rate_limit import enforce_daily_limit
from app.schemas import ActionTarget, LetterIn, LinkAccountIn, MatchOut, ProfileIn, ReportIn, TrustVoteIn
from app.services.background_refresh import background_refresh_loop, can_manual_refresh
from app.services.leaderboard import get_leaderboard, get_user_position, rebuild_all_leaderboards
from app.services.matching import next_candidate
from app.services.stats_refresh import refresh_user_stats
from app.services.trust import check_suspicion, check_vote_cooldown, compute_weighted_trust
from app.utils import build_profile_out

settings = get_settings()
app = FastAPI(title="Elyx API", version="0.1.0")

origins = [x.strip() for x in settings.cors_origin.split(",") if x.strip()]
# Always allow localhost and all Vercel preview URLs
ALWAYS_ALLOWED = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://*.vercel.app",
]
merged_origins = list(dict.fromkeys(ALWAYS_ALLOWED + origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=merged_origins if "*" not in merged_origins else ["*"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


_background_tasks: list[asyncio.Task] = []
SUPPORTED_ACCOUNT_PROVIDERS = ("riot", "steam", "faceit", "blizzard", "epic")
SUPPORTED_GAMES = (
    "Valorant",
    "CS2",
    "Dota 2",
    "League of Legends",
    "Fortnite",
    "Apex Legends",
    "PUBG",
    "Call of Duty / Warzone",
    "Rainbow Six Siege",
    "Overwatch 2",
    "Other",
)


@app.on_event("startup")
async def seed_games() -> None:
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception:
        if get_database_url().startswith("sqlite"):
            raise

    from app.database import SessionLocal

    async with SessionLocal() as session:
        existing_names = set((await session.execute(select(Game.name))).scalars().all())
        missing_games = [Game(name=name) for name in SUPPORTED_GAMES if name not in existing_names]
        if missing_games:
            session.add_all(missing_games)
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


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "elyx-backend", "status": "ok", "docs": "/docs"}


def _is_admin(user: User) -> bool:
    return user.tg_id in get_admin_ids()


def _as_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


async def _assert_not_blocked(db: AsyncSession, user_a: int, user_b: int) -> None:
    blocked = (
        await db.execute(
            select(Block.id).where(
                or_(
                    and_(Block.from_user_id == user_a, Block.to_user_id == user_b),
                    and_(Block.from_user_id == user_b, Block.to_user_id == user_a),
                )
            )
        )
    ).scalar_one_or_none()
    if blocked:
        raise HTTPException(status_code=403, detail="Interaction unavailable")


async def _reset_user_state(db: AsyncSession, user_id: int) -> None:
    await db.execute(delete(Profile).where(Profile.user_id == user_id))
    await db.execute(delete(Stats).where(Stats.user_id == user_id))
    await db.execute(delete(ExternalAccount).where(ExternalAccount.user_id == user_id))
    await db.execute(delete(LeaderboardEntry).where(LeaderboardEntry.user_id == user_id))
    await db.execute(delete(Like).where(or_(Like.from_user_id == user_id, Like.to_user_id == user_id)))
    await db.execute(delete(Skip).where(or_(Skip.from_user_id == user_id, Skip.to_user_id == user_id)))
    await db.execute(delete(Letter).where(or_(Letter.from_user_id == user_id, Letter.to_user_id == user_id)))
    await db.execute(delete(Match).where(or_(Match.user_a == user_id, Match.user_b == user_id)))
    await db.execute(delete(TrustVote).where(or_(TrustVote.from_user_id == user_id, TrustVote.to_user_id == user_id)))
    await db.execute(delete(Block).where(or_(Block.from_user_id == user_id, Block.to_user_id == user_id)))
    await db.execute(delete(Report).where(or_(Report.reporter_user_id == user_id, Report.target_user_id == user_id)))
    await db.commit()


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


@app.post("/profiles/me/reset")
async def reset_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _reset_user_state(db, current_user.id)
    return {"ok": True}


@app.get("/profiles/{user_id}")
async def get_profile(user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _ = current_user
    await _assert_not_blocked(db, current_user.id, user_id)
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
    await _assert_not_blocked(db, current_user.id, payload.target_user_id)

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
    await _assert_not_blocked(db, current_user.id, payload.target_user_id)

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
    await _assert_not_blocked(db, current_user.id, payload.target_user_id)

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
        blocked = (
            await db.execute(
                select(Block.id).where(
                    or_(
                        and_(Block.from_user_id == current_user.id, Block.to_user_id == other_id),
                        and_(Block.from_user_id == other_id, Block.to_user_id == current_user.id),
                    )
                )
            )
        ).scalar_one_or_none()
        if blocked:
            continue
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
    await _assert_not_blocked(db, current_user.id, other_id)
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
    await _assert_not_blocked(db, current_user.id, target_user_id)

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
    normalized_ref = _normalize_account_ref(provider, account_ref)
    if not normalized_ref:
        raise HTTPException(status_code=400, detail="Invalid account reference")

    row = (
        await db.execute(
            select(ExternalAccount).where(
                and_(ExternalAccount.user_id == user_id, ExternalAccount.provider == provider)
            )
        )
    ).scalar_one_or_none()
    if row:
        row.account_ref = normalized_ref
    else:
        db.add(ExternalAccount(user_id=user_id, provider=provider, account_ref=normalized_ref, verified=False))
    await db.commit()
    return {"ok": True, "provider": provider, "verified": False}


def _normalize_account_ref(provider: str, account_ref: str) -> str | None:
    value = (account_ref or "").strip()
    if not value:
        return None

    if provider == "riot":
        value = value.replace("＃", "#").replace("%23", "#")
        if value.count("#") != 1:
            return None
        name, tag = value.split("#", 1)
        if not name.strip() or not tag.strip():
            return None
        if len(name.strip()) > 32 or len(tag.strip()) > 16:
            return None
        return f"{name.strip()}#{tag.strip()}"

    if provider == "steam":
        if len(value) < 2:
            return None
        return value

    if provider in ("faceit", "blizzard", "epic"):
        if len(value) < 2 or len(value) > 128:
            return None
        return value

    return None


@app.get("/account/accounts")
async def list_linked_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = (
        await db.execute(
            select(ExternalAccount).where(ExternalAccount.user_id == current_user.id)
        )
    ).scalars().all()
    by_provider = {row.provider: row for row in rows}
    return [
        {
            "provider": provider,
            "account_ref": by_provider[provider].account_ref if provider in by_provider else None,
            "connected": provider in by_provider,
            "verified": bool(by_provider[provider].verified) if provider in by_provider else False,
        }
        for provider in SUPPORTED_ACCOUNT_PROVIDERS
    ]


@app.post("/actions/block")
async def action_block(
    payload: ActionTarget,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot block self")

    existing = (
        await db.execute(
            select(Block).where(
                and_(Block.from_user_id == current_user.id, Block.to_user_id == payload.target_user_id)
            )
        )
    ).scalar_one_or_none()
    if not existing:
        db.add(Block(from_user_id=current_user.id, to_user_id=payload.target_user_id))
        await db.commit()
    return {"ok": True}


@app.post("/actions/report")
async def action_report(
    payload: ReportIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot report self")

    db.add(
        Report(
            reporter_user_id=current_user.id,
            target_user_id=payload.target_user_id,
            reason=payload.reason.strip(),
        )
    )
    await db.commit()
    return {"ok": True}


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


@app.get("/reports/me")
async def my_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = (
        await db.execute(
            select(Report)
            .where(Report.reporter_user_id == current_user.id)
            .order_by(Report.created_at.desc())
            .limit(20)
        )
    ).scalars().all()
    return [
        {
            "report_id": row.id,
            "target_user_id": row.target_user_id,
            "reason": row.reason,
            "status": row.status,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@app.post("/leaderboard/rebuild")
async def leaderboard_rebuild(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Admin/service endpoint to rebuild all leaderboards."""
    results = await rebuild_all_leaderboards(db)
    return {"ok": True, "rebuilt": results}


@app.get("/admin/overview")
async def admin_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not _is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    active_cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_users = (await db.execute(select(func.count()).select_from(User))).scalar_one()
    active_users = (
        await db.execute(select(func.count()).select_from(User).where(User.last_active_at >= active_cutoff))
    ).scalar_one()
    profiles_created = (await db.execute(select(func.count()).select_from(Profile))).scalar_one()
    matches_created = (await db.execute(select(func.count()).select_from(Match))).scalar_one()
    open_reports = (
        await db.execute(select(func.count()).select_from(Report).where(Report.status == "open"))
    ).scalar_one()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "profiles_created": profiles_created,
        "matches_created": matches_created,
        "open_reports": open_reports,
    }


@app.get("/admin/reports")
async def admin_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not _is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")

    rows = (
        await db.execute(
            select(Report).order_by(
                case((Report.status == "open", 0), else_=1),
                Report.created_at.desc(),
            )
        )
    ).scalars().all()
    return [
        {
            "report_id": row.id,
            "reporter_user_id": row.reporter_user_id,
            "target_user_id": row.target_user_id,
            "reason": row.reason,
            "status": row.status,
            "created_at": row.created_at,
            "resolved_at": row.resolved_at,
            "resolved_by_tg_id": row.resolved_by_tg_id,
        }
        for row in rows
    ]


@app.post("/admin/reports/{report_id}/resolve")
async def admin_resolve_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not _is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")

    report = (await db.execute(select(Report).where(Report.id == report_id))).scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.status = "resolved"
    report.resolved_at = datetime.now(timezone.utc)
    report.resolved_by_tg_id = current_user.tg_id
    await db.commit()
    return {"ok": True}


# ===== Premium =====

@app.get("/premium/status")
async def premium_status(current_user: User = Depends(get_current_user)):
    is_active = current_user.is_premium
    days_left = 0
    premium_until = _as_utc(current_user.premium_until)
    if premium_until:
        delta = premium_until - datetime.now(timezone.utc)
        days_left = max(0, delta.days)
        if days_left == 0:
            is_active = False
    return {
        "is_premium": is_active,
        "premium_until": premium_until.isoformat() if premium_until else None,
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
