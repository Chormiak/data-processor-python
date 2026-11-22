from __future__ import annotations

from ..core.entidades import Configuracao
from ..core.metricas import calcular_medias_por_disciplina
from ..core.resultados import ResultadoProcessamento
from ..core.validador import validar_alunos, validar_notas
from ..infra.arquivos import FonteDados


def executar_processamento(fonte: FonteDados) -> ResultadoProcessamento:
    """Executa validação e consolidação sem conhecer a origem dos dados."""
    configuracao = Configuracao.a_partir_de_dict(fonte.carregar_config())

    alunos, erros_alunos = validar_alunos(fonte.carregar_alunos())
    matriculas_validas = {aluno.matricula for aluno in alunos}
    notas, erros_notas = validar_notas(
        fonte.carregar_notas(),
        matriculas_validas,
        configuracao.nota_maxima,
    )

    alunos_por_matricula = {aluno.matricula: aluno for aluno in alunos}
    for nota in notas:
        alunos_por_matricula[nota.matricula].notas.append(nota)

    return ResultadoProcessamento(
        alunos=alunos,
        notas=notas,
        erros_alunos=erros_alunos,
        erros_notas=erros_notas,
        medias_disciplinas=calcular_medias_por_disciplina(notas),
        configuracao=configuracao,
    )
