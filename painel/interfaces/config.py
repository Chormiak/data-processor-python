from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    data_dir: Path
    log_level: str = "INFO"


def obter_settings() -> Settings:
    """Carrega configurações externas, sem fixar caminhos no código da API."""
    nivel = os.environ.get("PAINEL_LOG_LEVEL", "INFO").upper()
    if not isinstance(getattr(logging, nivel, None), int):
        nivel = "INFO"
    return Settings(
        data_dir=Path(os.environ.get("PAINEL_DATA_DIR", "data")),
        log_level=nivel,
    )
