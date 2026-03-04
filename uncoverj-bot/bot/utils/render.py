from backend.models.profile import Profile
from backend.models.stats import StatsSnapshot

def render_profile_text(profile: Profile, stats: StatsSnapshot | None, is_premium: bool, trust_up: int, trust_down: int) -> str:
    """Генерация текста анкеты по формату PRD"""
    premium_star = " ⭐" if is_premium else ""
    gender_map = {"male": "Парень", "female": "Девушка", "hidden": "Скрыто"}
    gender_str = gender_map.get(profile.gender, "Скрыто")
    
    text = f"👤 <b>{profile.nickname}</b>, {profile.age}, {gender_str}{premium_star}\n"
    
    game_map = {"valorant": "Valorant", "cs2": "CS2", "dota2": "Dota 2", "lol": "LoL"}
    game_str = game_map.get(profile.game_primary, "Game")
    tags = ", ".join(profile.playstyle_tags) if profile.playstyle_tags else "Без тегов"
    text += f"🎮 {game_str} • {tags}\n"
    
    if stats and stats.source_status == "ok":
        kd = round(stats.kd_ratio, 2) if stats.kd_ratio else 0.0
        rank = stats.rank_text or "Unranked"
        winrate = round(stats.winrate * 100, 1) if stats.winrate else 0.0
        score = stats.unified_score or 0
        text += f"📊 K/D: {kd} | Rank: {rank} | Win%: {winrate}%\n"
        text += f"🏆 Score: {score}\n"
    elif stats and stats.source_status == "private":
        text += "📊 Профиль закрыт настройками приватности\n"
        text += "🏆 Score: 0\n"
    else:
        text += "📊 Статистика пока не загружена\n"
        text += "🏆 Score: 0\n"
        
    text += f"🤝 Trust: 👍 {trust_up} | 🗑 {trust_down}\n"
    
    if profile.bio_text:
        text += f"\n💬 {profile.bio_text}"
        
    return text
