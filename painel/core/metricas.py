from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from .entidades import Nota


def calcular_medias_por_disciplina(notas: Iterable[Nota]) -> dict[str, float]:
    """Calcula a média de cada disciplina considerando todas as turmas."""
    valores: dict[str, list[float]] = defaultdict(list)
    for nota in notas:
        valores[nota.disciplina].append(nota.nota)

    return {
        disciplina: sum(notas_disciplina) / len(notas_disciplina)
        for disciplina, notas_disciplina in sorted(valores.items())
    }
