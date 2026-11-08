"""Mini Git 커밋 객체: 파일 내용이 아닌 메타데이터만 추적한다."""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Commit:
    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: list[str] = field(default_factory=list)
