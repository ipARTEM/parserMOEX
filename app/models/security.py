from pydantic import BaseModel
from typing import Optional

class SecurityQuote(BaseModel):
    """Единая модель котировки инструмента для тепловой карты."""
    secid: str                 # Тикер, напр. SBER, IMOEXF
    shortname: str             # Короткое название
    last: Optional[float]      # Последняя цена
    prevprice: Optional[float] # Предыдущая цена (для акций) или PREVSETTLEPRICE (для фьючерсов)
    pct_change: Optional[float]# Изменение, % (last vs prevprice)
    board: str                 # Режим торгов (борд), напр. TQBR, RFUD
    engine: str                # Движок: stock / futures
    market: str                # Рынок: shares / forts
    value: Optional[float] = None   # Оборот в рублях за сегодня, если доступен
    volume: Optional[float] = None  # Объем, если доступен