# Задача для Антигравити: Исправить навигацию и проверить API

## 1. Исправить иконки навигации (bottom-nav.tsx)
**Проблема:** Иконки серые и не переключаются на другие страницы.

**Что нужно:**
- Сделать иконки цветными под тематику игры (как в page.tsx)
- Добавить рабочие переходы на страницы:
  - Матчи (matches)
  - Лидеры (leaderboard)  
  - Настройки (settings)
  - Профиль (profile) — уже есть

**Стили:** Использовать GAME_THEMES из page.tsx для каждой игры

## 2. Проверить работу всех API
**Последовательно проверить:**

### Valorant API
- Ключ: HDEV-addbd95e-b174-4a9d-95dd-f9d0850d9411
- Тест: `curl -H "Authorization: HDEV-addbd95e..." https://api.henrikdev.xyz/valorant/v1/account/Uncoverj/1795`
- Ожидаемый результат: 404 (аккаунт есть, но нет матчей) — это ОК

### Faceit API  
- Ключ: 99c9beba-57ee-482f-aa38-a85810d40e31
- Тест: `curl -H "Authorization: Bearer 99c9beba..." https://api.faceit.com/players/v1/nicknames/{nickname}`
- Ожидаемый результат: 200 или 404 (если ник не найден) — оба ОК

### Riot API
- Ключ: RGAPI-c7ba0fb3-992a-4107-9c59-52fc764d691a (истёк)
- Нужен свежий ключ с developer.riotgames.com
- Тест: `curl "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}"`

## 3. Детальный гайд если API не работают
**Для каждого API предоставить:**
1. Где взять ключ (ссылка)
2. Как добавить в .env
3. Команды для перезапуска
4. Тестовые запросы для проверки

## 4. Проверить полный цикл
**Проверить сценарий:**
1. Пользователь в Telegram боте вводит Riot ID/Faceit ник
2. Бот вызывает /account/link/{provider}
3. Бот вызывает /account/refresh-stats  
4. Backend запрашивает API
5. Результат сохраняется в Stats
6. Вебапп показывает статистику

**Результат:** Отчёт что работает, что нет и как исправить.

## Файлы для работы:
- `webapp/components/bottom-nav.tsx` — навигация
- `webapp/app/page.tsx` — пример GAME_THEMES
- `backend/.env` — API ключи
- `backend/app/services/` — модули API
- `bot/app/handlers.py` — обработка ошибок

**Важно:** Не менять основную логику, только исправить навигацию и диагностировать API.
