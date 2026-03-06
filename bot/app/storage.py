from collections import defaultdict


current_candidates: dict[int, int] = {}
registration_drafts: dict[int, dict] = defaultdict(dict)
letters_target: dict[int, int] = {}
matches_cache: dict[int, list[dict]] = defaultdict(list)
matches_index: dict[int, int] = defaultdict(int)
pending_reactions: dict[int, int] = {}
custom_first_move_target: dict[int, int] = {}
