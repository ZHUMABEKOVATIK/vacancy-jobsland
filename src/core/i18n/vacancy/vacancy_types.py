from dataclasses import dataclass
from typing import Optional

@dataclass
class TgPost:
    text: str
    photo_path: Optional[str] = None
    parse_mode: str = "HTML"