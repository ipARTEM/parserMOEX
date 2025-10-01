# app/main.py
import asyncio
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import TEMPLATES_DIR, STATIC_DIR, STOCK_BOARD, FUTURES_BOARD
from app.services.moex_client import MoexClient
from app.services.heatmap_service import HeatmapService

app = FastAPI(title="parserMOEX", version="1.0.0", docs_url="/docs", redoc_url=None)

# Подключаем статику и шаблоны
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Сервис для теплокарт
heatmaps = HeatmapService(max_abs_percent=5.0)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> Any:
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/parser", response_class=HTMLResponse)
async def parser_page(request: Request) -> Any:
    """Страница с тепловыми картами Акций и Фьючерсов (онлайн из ISS)."""
    async with MoexClient() as client:
        shares_task = asyncio.create_task(client.get_shares_quotes(board=STOCK_BOARD))
        futures_task = asyncio.create_task(client.get_futures_quotes(board=FUTURES_BOARD))
        shares_quotes, futures_quotes = await asyncio.gather(shares_task, futures_task)

    shares_tiles = heatmaps.to_tile_dicts(shares_quotes, limit=120)
    futures_tiles = heatmaps.to_tile_dicts(futures_quotes, limit=120)

    ctx: Dict[str, Any] = {
        "request": request,
        "shares_tiles": shares_tiles,
        "futures_tiles": futures_tiles,
        "shares_board": STOCK_BOARD,
        "futures_board": FUTURES_BOARD,
    }
    return templates.TemplateResponse("heatmap.html", ctx)

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request) -> Any:
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/howto", response_class=HTMLResponse)
async def howto(request: Request) -> Any:
    return templates.TemplateResponse("howto.html", {"request": request})

@app.get("/schedule", response_class=HTMLResponse)
async def schedule(request: Request) -> Any:
    return templates.TemplateResponse("schedule.html", {"request": request})
