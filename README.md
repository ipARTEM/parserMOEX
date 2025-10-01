# parserMOEX — локальный сайт с тепловыми картами MOEX

Современный мини‑сайт на FastAPI (Python) с кнопкой **parserMOEX** на главной. 
При нажатии загружается страница с тепловыми картами **Акций (TQBR)** и **Фьючерсов (FORTS)**.
Данные берутся онлайн из **ISS MOEX API**.

## 1) Куда положить проект

Разместите папку в `D:\parserMOEX` (или распакуйте архив туда). Структура:
```text
D:\parserMOEX
  ├─ app\
  │   ├─ main.py
  │   ├─ config.py
  │   ├─ models\security.py
  │   └─ services\(moex_client.py, heatmap_service.py)
  ├─ templates\(html-шаблоны)
  ├─ static\css, static\js
  ├─ requirements.txt
  └─ run.bat
```

## 2) Установка окружения (Windows)

Откройте **PowerShell**:
```powershell
cd D:\parserMOEX
py -3 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## 3) Запуск локального сервера (порт 8089)

В PowerShell (при активном venv):
```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8089 --reload
```
или дважды кликните `run.bat`.

Откройте в браузере: <http://127.0.0.1:8089/>

## 4) Как это работает (кратко)

- `MoexClient` запрашивает у ISS две таблицы для каждого рынка: 
  - `securities` — справочная информация (`SECID`, `SHORTNAME`, `PREVPRICE` / `PREVSETTLEPRICE`),
  - `marketdata` — цены и обороты (`LAST`, `VALTODAY`/`VOLTODAY`, `OPEN`, ...).
- Для каждой бумаги рассчитывается изменение в %: `(LAST - PREVPRICE) / PREVPRICE * 100` 
  (для фьючерсов используется `PREVSETTLEPRICE`, если `PREVPRICE` отсутствует).
- `HeatmapService` преобразует список котировок в плитки с цветом/насыщенностью по величине изменения.
- Шаблон `heatmap.html` рисует две сетки (Акции / Фьючерсы).

## 5) Куда смотреть/редактировать

- Настройки рынков/бордов: `app/config.py` (по умолчанию: TQBR и RFUD).
- Логика запроса к ISS: `app/services/moex_client.py`.
- Расчёт цветов/интенсивности: `app/services/heatmap_service.py`.
- Верстка и стили: `templates/*.html`, `static/css/styles.css`.

## 6) Частые вопросы

- **Можно ли расширить список полей ISS?** Да, отредактируйте параметры `*.columns` в `moex_client.py`.
- **Как обновлять данные?** Просто перезагрузите страницу `/parser`.
- **Что делать при ошибке сети?** Проверьте интернет/VPN, повторите попытку.

---

© parserMOEX — локальная учебная сборка.