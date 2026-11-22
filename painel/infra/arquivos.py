from __future__ import annotations

import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path

from .tipos import RegistroComLinha


class FonteDados(ABC):
    """Porta de entrada para as fontes de dados do processamento."""

    @abstractmethod
    def carregar_alunos(self) -> list[RegistroComLinha]:
        raise NotImplementedError

    @abstractmethod
    def carregar_notas(self) -> list[RegistroComLinha]:
        raise NotImplementedError

    @abstractmethod
    def carregar_config(self) -> dict[str, object]:
        raise NotImplementedError


class FonteDadosArquivos(FonteDados):
    def __init__(
        self,
        caminho_alunos: str | Path,
        caminho_notas: str | Path,
        caminho_config: str | Path,
    ) -> None:
        self.caminho_alunos = Path(caminho_alunos)
        self.caminho_notas = Path(caminho_notas)
        self.caminho_config = Path(caminho_config)

    @staticmethod
    def _carregar_csv(caminho: Path) -> list[RegistroComLinha]:
        registros: list[RegistroComLinha] = []
        with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
            leitor = csv.DictReader(arquivo)
            if leitor.fieldnames is None:
                return registros
            for registro in leitor:
                registros.append((leitor.line_num, dict(registro)))
        return registros

    def carregar_alunos(self) -> list[RegistroComLinha]:
        return self._carregar_csv(self.caminho_alunos)

    def carregar_notas(self) -> list[RegistroComLinha]:
        return self._carregar_csv(self.caminho_notas)

    def carregar_config(self) -> dict[str, object]:
        with self.caminho_config.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        if not isinstance(dados, dict):
            raise ValueError("config.json deve conter um objeto JSON")
        return dados


class FonteDadosMemoria(FonteDados):
    """Fonte para testes e requisições que já recebem dados em memória."""

    def __init__(
        self,
        alunos: list[dict[str, object]],
        notas: list[dict[str, object]],
        config: dict[str, object],
    ) -> None:
        self._alunos = alunos
        self._notas = notas
        self._config = config

    @staticmethod
    def _com_linhas(registros: list[dict[str, object]]) -> list[RegistroComLinha]:
        # Linha 1 é o cabeçalho, inclusive para manter o contrato dos CSVs.
        return [(indice + 2, dict(registro)) for indice, registro in enumerate(registros)]

    def carregar_alunos(self) -> list[RegistroComLinha]:
        return self._com_linhas(self._alunos)

    def carregar_notas(self) -> list[RegistroComLinha]:
        return self._com_linhas(self._notas)

    def carregar_config(self) -> dict[str, object]:
        return dict(self._config)
