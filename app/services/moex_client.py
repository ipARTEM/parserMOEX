import asyncio
from typing import Dict, List, Optional
from urllib.parse import urlencode

import httpx

from app.config import (
    ISS_BASE_URL,
    HTTP_TIMEOUT,
)
from app.models.security import SecurityQuote

class MoexClient:
    """Клиент для ISS MOEX API (https://iss.moex.com).
    Выполняет запросы и приводит ответы к удобным структурам.
    """

    def __init__(self, base_url: str = ISS_BASE_URL, timeout: float = HTTP_TIMEOUT) -> None:
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def fetch_json(self, path: str, params: Optional[Dict[str, str]] = None) -> Dict:
        """Выполняет GET запрос к ISS и возвращает JSON."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_board_quotes(self, *, engine: str, market: str, board: str) -> List[SecurityQuote]:
        """Возвращает список котировок по указанному рынку/борду.
        Мы запрашиваем сразу 2 таблицы: 'securities' (справочник) и 'marketdata' (текущие данные).
        Поля ограничиваем через *columns*, чтобы не тянуть лишнее.
        """
        # Таблица описаний
        sec_params = {
            "iss.only": "securities",
            # Берем тикер, короткое имя и предыдущую цену.
            "securities.columns": "SECID,SHORTNAME,PREVPRICE,PREVSETTLEPRICE"
        }
        md_params = {
            "iss.only": "marketdata",
            # LAST - последняя цена; VALTODAY/VOLTODAY - обороты (не всегда есть)
            "marketdata.columns": "SECID,LAST,VALTODAY,VOLTODAY,OPEN,HIGH,LOW"
        }

        sec_path = f"iss/engines/{engine}/markets/{market}/boards/{board}/securities.json"
        md_path  = f"iss/engines/{engine}/markets/{market}/boards/{board}/securities.json"

        sec_json, md_json = await asyncio.gather(
            self.fetch_json(sec_path, sec_params),
            self.fetch_json(md_path, md_params)
        )

        # Парсим таблицу securities
        sec_table = sec_json.get("securities", {})
        sec_cols = sec_table.get("columns", [])
        sec_data = sec_table.get("data", [])
        idx_secid = sec_cols.index("SECID") if "SECID" in sec_cols else None
        idx_short = sec_cols.index("SHORTNAME") if "SHORTNAME" in sec_cols else None
        idx_prev  = sec_cols.index("PREVPRICE") if "PREVPRICE" in sec_cols else None
        idx_prev_settle = sec_cols.index("PREVSETTLEPRICE") if "PREVSETTLEPRICE" in sec_cols else None

        info: Dict[str, Dict] = {}
        for row in sec_data:
            if idx_secid is None:
                continue
            secid = row[idx_secid]
            shortname = row[idx_short] if idx_short is not None else secid
            # Для акций PREVPRICE, для фьючерсов чаще PREVSETTLEPRICE
            prevprice = None
            if idx_prev is not None and row[idx_prev] is not None:
                prevprice = row[idx_prev]
            elif idx_prev_settle is not None and row[idx_prev_settle] is not None:
                prevprice = row[idx_prev_settle]
            info[secid] = {
                "shortname": shortname,
                "prevprice": prevprice,
            }

        # Парсим marketdata
        md_table = md_json.get("marketdata", {})
        md_cols = md_table.get("columns", [])
        md_data = md_table.get("data", [])
        idx_m_secid = md_cols.index("SECID") if "SECID" in md_cols else None
        idx_last    = md_cols.index("LAST") if "LAST" in md_cols else None
        idx_val     = md_cols.index("VALTODAY") if "VALTODAY" in md_cols else None
        idx_vol     = md_cols.index("VOLTODAY") if "VOLTODAY" in md_cols else None

        quotes: List[SecurityQuote] = []
        for row in md_data:
            if idx_m_secid is None:
                continue
            secid = row[idx_m_secid]
            last = row[idx_last] if (idx_last is not None) else None
            valtoday = row[idx_val] if (idx_val is not None) else None
            voltoday = row[idx_vol] if (idx_vol is not None) else None

            shortname = info.get(secid, {}).get("shortname", secid)
            prevprice = info.get(secid, {}).get("prevprice")

            pct_change = None
            if last is not None and prevprice not in (None, 0):
                try:
                    pct_change = (last - prevprice) / prevprice * 100.0
                except Exception:
                    pct_change = None

            quotes.append(SecurityQuote(
                secid=secid,
                shortname=shortname,
                last=last,
                prevprice=prevprice,
                pct_change=pct_change,
                board=board,
                engine=engine,
                market=market,
                value=valtoday,
                volume=voltoday,
            ))

        # Очищаем список: оставим те, у кого есть last и pct_change
        filtered = [q for q in quotes if q.last is not None and q.pct_change is not None]
        # Чтобы тепловая карта не была перегружена: сортируем по обороту, если есть, иначе по |%|
        filtered.sort(key=lambda q: (q.value if q.value is not None else abs(q.pct_change)), reverse=True)
        return filtered

    async def get_shares_quotes(self, board: str = "TQBR") -> List[SecurityQuote]:
        return await self.get_board_quotes(engine="stock", market="shares", board=board)

    async def get_futures_quotes(self, board: str = "RFUD") -> List[SecurityQuote]:
        return await self.get_board_quotes(engine="futures", market="forts", board=board)