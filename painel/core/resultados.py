from __future__ import annotations

from dataclasses import dataclass

from .entidades import Aluno, Configuracao, ErroRegistro, Nota


@dataclass(slots=True)
class ResultadoProcessamento:
    alunos: list[Aluno]
    notas: list[Nota]
    erros_alunos: list[ErroRegistro]
    erros_notas: list[ErroRegistro]
    medias_disciplinas: dict[str, float]
    configuracao: Configuracao

    @property
    def erros(self) -> list[ErroRegistro]:
        return [*self.erros_alunos, *self.erros_notas]

    @property
    def total_erros(self) -> int:
        return len(self.erros_alunos) + len(self.erros_notas)

    @property
    def total_notas_invalidas(self) -> int:
        return len(self.erros_notas)
