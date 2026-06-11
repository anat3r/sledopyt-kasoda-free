# Разработка модуля «Альтернативный Следопыт»

## Ветки

| Ветка | Назначение | Правила |
|---|---|---|
| `main` | Стабильный код, с которого выходят релизы | Защищённая. Только через PR. Каждый релиз помечается тегом `vX.Y.Z`. |
| `develop` | Интеграционная ветка текущей разработки | Сюда вливаются батчи. CI обязан быть зелёным. |
| `feature/*` | Отдельная задача/батч | Ответвляется от `develop`, вливается обратно PR-ом. Напр. `feature/batch2-gloomstalker-monsterslayer`. |

**Поток:** `feature/*` → PR в `develop` (CI: `validate` + `pack`) → когда батч стабилен, PR `develop` → `main` → создать Release с тегом `vX.Y.Z` → workflow `release.yml` сам соберёт и опубликует.

## Источник истины

- **`src/**/*.json`** — это источник истины (ревьюится в PR).
- **`packs/`** — собирается из `src/` (в `.gitignore`, не коммитится; в релиз попадает собранным).
- **`tools/build.py`, `tools/build_subclasses.py`** — опциональные Python-генераторы для массового авторинга. Запускаются локально, пишут в `src/`, результат коммитится. CI их НЕ запускает (собирает только Node).

## Команды

```bash
npm ci                 # установить зависимости (Foundry CLI)
npm run generate       # (опц.) перегенерировать src/ из Python-генераторов
npm run validate       # проверка: уникальные _id, формат _key, внутренние ссылки
npm run pack           # скомпилировать src/ -> packs/ (LevelDB)
npm run build          # validate + pack
```

> Проверка существования внешних UUID (заклинания/боевые стили из Laaru) — **локальная**: CI не имеет доступа к платному паку Laaru, поэтому `validate.mjs` проверяет только внутреннюю целостность. Резолв Laaru-UUID делайте у себя, где Laaru распакован.

## Выпуск релиза

1. Влейте `develop` → `main`.
2. На GitHub: **Releases → Draft a new release**, тег `vX.Y.Z` (semver; новый батч = minor).
3. **Publish.** `release.yml` сам: проставит версию и `download` в `module.json` (из тега и `github.repository`), соберёт паки, сделает `module.zip` и приложит `module.json` + `module.zip` к релизу.
4. Ссылка для установки (неизменная): `https://github.com/<owner>/<repo>/releases/latest/download/module.json`.

`manifest` всегда «latest», `download` всегда на конкретную версию — не указывайте zip ветки.

## Development project (доска)

Рекомендуется GitHub Project (Projects v2) с колонками **Backlog → In progress → Review → Done**. Заведите по issue на оставшиеся батчи подклассов (шаблон `subclass-batch`):

- Батч 2 — Сумрачный охотник + Убийца чудовищ
- Батч 3 — Странник горизонта + Странник фей
- Батч 4 — Хранитель роя + Зимний ходок + Мастер ловушек
- Батч 5 — Повелитель зверей + Наездник на драконе (Actor-компаньоны)
