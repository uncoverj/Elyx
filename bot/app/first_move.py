"""First Move Generator — suggests 3 context-aware opening messages after a match.

Uses shared game + overlapping tags/roles to build personalized icebreakers.
"""

import random

# Templates organized by game
_GAME_OPENERS: dict[str, list[str]] = {
    "valorant": [
        "Го дуо ранк? Обещаю не рашить без смоков 😅",
        "Привет! Наконец кто-то с нормальным рангом. Какой агент мейн?",
        "Эй, мэтч! Я обычно играю {role}. Нужен кто-то на {their_role}?",
        "Ну что, покажем что два {rank} вместе — это сила? 🔥",
        "Привет! K/D у тебя красивый. Покатаем?",
    ],
    "cs2": [
        "Привет! Давно искал адекватного напарника на ранки 🎯",
        "Го катку? Обещаю коллить нормально 😂",
        "Мэтч! Какие карты любишь? Я за Mirage всегда ✌️",
        "Ну наконец! Адекват в CS2 — это редкость. Го в лобби?",
    ],
    "dota 2": [
        "Привет! Ты на какой позиции обычно? Я {role} мейн",
        "Го катку! Обещаю не пикать Пуджа на мид 😅",
        "Мэтч! Адекватные игроки в доте — на вес золота 💎",
        "Покатаем? Мне нужен хороший {their_role} в тиме",
    ],
    "league of legends": [
        "Привет! Какой лейн мейнишь? Я обычно {role}",
        "Го дуо? Обещаю не интить 😂",
        "Наконец адекватный тиммейт! Покатаем ранк?",
        "Мэтч! Кого мейнишь? Может, у нас крутой синерджи 🔥",
    ],
}

_GENERIC_OPENERS = [
    "Привет! Рада мэтчу. Что обычно играешь? 😊",
    "Мэтч! Расскажи про себя — что за вайб? 🎮",
    "Привет! Наконец кто-то интересный. Когда обычно играешь?",
    "Эй, мэтч! Давай знакомиться? Я {nickname} ✌️",
]

# Tag-based bonuses
_TAG_OPENERS = {
    "флирт ок": "Кстати, анкета у тебя огонь 😏🔥",
    "чилл": "Вайб у тебя прям мой — чилл и без напряга 😌",
    "серьёзный": "Вижу серьёзный подход — уважаю! Го покатаем? 💪",
    "войс": "Го в войс? Так намного веселее 🎤",
}


def generate_first_moves(
    my_profile: dict,
    their_profile: dict,
) -> list[str]:
    """Generate 3 first-message suggestions based on shared context.

    Args:
        my_profile: current user's profile dict from API
        their_profile: matched user's profile dict from API

    Returns:
        list of 3 suggested messages
    """
    game = (their_profile.get("game_name") or "").lower()
    my_roles = my_profile.get("roles") or []
    their_roles = their_profile.get("roles") or []
    my_tags = my_profile.get("tags") or []
    their_tags = their_profile.get("tags") or []
    my_nick = my_profile.get("nickname", "")

    # Get game-specific pool
    pool = list(_GAME_OPENERS.get(game, _GENERIC_OPENERS))
    pool.extend(_GENERIC_OPENERS)

    # Replace placeholders
    results = []
    for tmpl in pool:
        msg = tmpl
        if "{role}" in msg and my_roles:
            msg = msg.replace("{role}", my_roles[0])
        if "{their_role}" in msg and their_roles:
            msg = msg.replace("{their_role}", their_roles[0])
        if "{nickname}" in msg:
            msg = msg.replace("{nickname}", my_nick)
        if "{rank}" in msg:
            stats = their_profile.get("stats") or {}
            rank = stats.get("rank_name") or "геймер"
            msg = msg.replace("{rank}", rank)
        results.append(msg)

    # Add a tag-based opener if there's overlap
    shared_tags = set(t.lower() for t in my_tags) & set(t.lower() for t in their_tags)
    for tag, opener in _TAG_OPENERS.items():
        if tag in shared_tags:
            results.append(opener)
            break

    # Shuffle and pick 3 unique ones
    random.shuffle(results)
    seen = set()
    final = []
    for msg in results:
        if msg not in seen:
            seen.add(msg)
            final.append(msg)
        if len(final) == 3:
            break

    return final if final else [
        "Привет! Рада мэтчу 😊",
        "Го катку? 🎮",
        "Привет! Расскажи о себе 💬",
    ]
