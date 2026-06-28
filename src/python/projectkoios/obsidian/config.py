from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VaultConfiguration:
    path: Path | None = None
