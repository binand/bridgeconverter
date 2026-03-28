from dataclasses import dataclass
from typing import Optional

@dataclass
class DealEntry:
    lin: str
    contract: Optional[str] = None
    declarer: Optional[str] = None
    result: Optional[str] = None
    lead: Optional[str] = None
    score: Optional[str] = None
