from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite


@dataclass(slots=True, frozen=True)
class Nota:
    matricula: int
    disciplina: str
    avaliacao: str
    nota: float


@dataclass(slots=True)
class Aluno:
    matricula: int
    nome: str
    turma: str
    notas: list[Nota] = field(default_factory=list)

    def media(self) -> float | None:
        """Retorna a média aritmética das notas válidas, sem arredondamento."""
        if not self.notas:
            return None
        return sum(nota.nota for nota in self.notas) / len(self.notas)

    def situacao(self, media_aprovacao: float, media_recuperacao: float) -> str:
        """Determina a situação usando a média original, não a média formatada."""
        media = self.media()
        if media is None:
            return "sem notas"
        if media >= media_aprovacao:
            return "aprovado"
        if media >= media_recuperacao:
            return "recuperação"
        return "reprovado"


@dataclass(slots=True, frozen=True)
class ErroRegistro:
    arquivo: str
    linha: int
    tipo: str
    mensagem: str


@dataclass(slots=True, frozen=True)
class Configuracao:
    media_aprovacao: float
    media_recuperacao: float
    nota_maxima: float

    @classmethod
    def a_partir_de_dict(cls, dados: dict[str, object]) -> "Configuracao":
        """Converte a configuração lida pela infraestrutura para tipos do domínio."""
        try:
            configuracao = cls(
                media_aprovacao=float(dados["media_aprovacao"]),
                media_recuperacao=float(dados["media_recuperacao"]),
                nota_maxima=float(dados["nota_maxima"]),
            )
        except (KeyError, TypeError, ValueError) as erro:
            raise ValueError(f"Configuração inválida: {erro}") from erro

        if not all(
            isfinite(valor)
            for valor in (
                configuracao.media_aprovacao,
                configuracao.media_recuperacao,
                configuracao.nota_maxima,
            )
        ):
            raise ValueError("Configuração inválida: as médias e a nota máxima devem ser finitas")
        if configuracao.nota_maxima <= 0:
            raise ValueError("Configuração inválida: nota_maxima deve ser maior que zero")
        if configuracao.media_recuperacao > configuracao.media_aprovacao:
            raise ValueError(
                "Configuração inválida: media_recuperacao não pode superar media_aprovacao"
            )
        if configuracao.media_aprovacao > configuracao.nota_maxima:
            raise ValueError("Configuração inválida: media_aprovacao supera nota_maxima")
        return configuracao
