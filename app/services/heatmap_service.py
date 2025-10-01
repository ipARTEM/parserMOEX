from typing import Iterable, List, Dict, Any
from math import tanh

from app.models.security import SecurityQuote

class HeatmapService:
    """Формирует данные для визуализации тепловых карт.
    Цвет кодируется по pct_change: зелёный — рост, красный — падение.
    Интенсивность ограничиваем сигмоидой/tanh, чтобы экстремальные значения не "жгли" экран.
    """
    def __init__(self, max_abs_percent: float = 5.0) -> None:
        # Нормировка: 100% интенсивности соответствует |pct| == max_abs_percent
        self.max_abs_percent = max_abs_percent

    def _pct_to_intensity(self, pct: float) -> float:
        # Используем tanh для мягкой нормировки
        x = max(-self.max_abs_percent, min(self.max_abs_percent, pct))
        return abs(tanh(x / self.max_abs_percent))

    def _color_for_pct(self, pct: float) -> str:
        # Возвращаем цвет в формате HSL: зелёный (120deg) для >0, красный (0deg) для <0.
        # Светлота по интенсивности.
        intensity = self._pct_to_intensity(pct)
        hue = 120 if pct >= 0 else 0
        # Чем больше интенсивность, тем темнее плитка (меньше светлоты)
        lightness = 80 - int(50 * intensity)  # 80% .. 30%
        return f"hsl({hue}, 60%, {lightness}%)"

    def to_tile_dicts(self, quotes: Iterable[SecurityQuote], limit: int = 100) -> List[Dict[str, Any]]:
        tiles: List[Dict[str, Any]] = []
        for q in list(quotes)[:limit]:
            color = self._color_for_pct(q.pct_change or 0.0)
            tiles.append({
                "secid": q.secid,
                "shortname": q.shortname,
                "last": q.last,
                "pct_change": q.pct_change,
                "value": q.value,
                "volume": q.volume,
                "color": color,
            })
        return tiles