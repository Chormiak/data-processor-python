from __future__ import annotations

import math
from collections.abc import Iterable

from .entidades import Aluno, ErroRegistro, Nota

RegistroComLinha = tuple[int, dict[str, object]]


def _texto(valor: object) -> str:
    if valor is None:
        return ""
    return str(valor).strip()


def _tem_campo_vazio(registro: dict[str, object], campos: tuple[str, ...]) -> bool:
    return any(not _texto(registro.get(campo)) for campo in campos)


def validar_alunos(registros: Iterable[RegistroComLinha]) -> tuple[list[Aluno], list[ErroRegistro]]:
    """Valida alunos sem interromper o processamento das linhas seguintes."""
    alunos: list[Aluno] = []
    erros: list[ErroRegistro] = []
    matriculas_vistas: set[int] = set()
    campos_obrigatorios = ("matricula", "nome", "turma")

    for linha, registro in registros:
        matricula_texto = _texto(registro.get("matricula"))
        nome = _texto(registro.get("nome"))
        turma = _texto(registro.get("turma"))

        # A ordem de validação é parte do contrato da especificação.
        if _tem_campo_vazio(registro, campos_obrigatorios):
            erros.append(
                ErroRegistro(
                    "alunos.csv",
                    linha,
                    "campo_vazio",
                    f"campo obrigatório vazio na linha {linha}",
                )
            )
            continue

        try:
            matricula = int(matricula_texto)
        except ValueError:
            erros.append(
                ErroRegistro(
                    "alunos.csv",
                    linha,
                    "matricula_invalida",
                    f"matrícula não numérica ({matricula_texto!r})",
                )
            )
            continue

        if matricula in matriculas_vistas:
            erros.append(
                ErroRegistro(
                    "alunos.csv",
                    linha,
                    "matricula_duplicada",
                    f"matrícula {matricula} já cadastrada",
                )
            )
            continue

        matriculas_vistas.add(matricula)
        alunos.append(Aluno(matricula=matricula, nome=nome, turma=turma))

    return alunos, erros


def validar_notas(
    registros: Iterable[RegistroComLinha],
    matriculas_validas: set[int],
    nota_maxima: float,
) -> tuple[list[Nota], list[ErroRegistro]]:
    """Valida notas na ordem definida e preserva a primeira ocorrência válida."""
    notas: list[Nota] = []
    erros: list[ErroRegistro] = []
    chaves_vistas: set[tuple[int, str, str]] = set()
    campos_obrigatorios = ("matricula", "disciplina", "avaliacao", "nota")

    for linha, registro in registros:
        matricula_texto = _texto(registro.get("matricula"))
        disciplina = _texto(registro.get("disciplina"))
        avaliacao = _texto(registro.get("avaliacao"))
        nota_texto = _texto(registro.get("nota"))

        if _tem_campo_vazio(registro, campos_obrigatorios):
            erros.append(
                ErroRegistro(
                    "notas.csv",
                    linha,
                    "campo_vazio",
                    f"campo obrigatório vazio na linha {linha}",
                )
            )
            continue

        try:
            valor_nota = float(nota_texto)
        except ValueError:
            erros.append(
                ErroRegistro(
                    "notas.csv",
                    linha,
                    "nota_invalida",
                    f"nota inválida ({nota_texto!r})",
                )
            )
            continue

        if not math.isfinite(valor_nota):
            erros.append(
                ErroRegistro(
                    "notas.csv",
                    linha,
                    "nota_invalida",
                    f"nota inválida ({nota_texto!r})",
                )
            )
            continue

        if valor_nota < 0 or valor_nota > nota_maxima:
            erros.append(
                ErroRegistro(
                    "notas.csv",
                    linha,
                    "nota_fora_do_intervalo",
                    f"nota {valor_nota:g} fora do intervalo de 0 a {nota_maxima:g}",
                )
            )
            continue

        try:
            matricula = int(matricula_texto)
        except ValueError:
            matricula = -1

        if matricula not in matriculas_validas:
            erros.append(
                ErroRegistro(
                    "notas.csv",
                    linha,
                    "matricula_inexistente",
                    f"matrícula inexistente ({matricula_texto})",
                )
            )
            continue

        chave = (matricula, disciplina, avaliacao)
        if chave in chaves_vistas:
            erros.append(
                ErroRegistro(
                    "notas.csv",
                    linha,
                    "avaliacao_duplicada",
                    (
                        f"avaliação {avaliacao} de {disciplina} já lançada "
                        f"para a matrícula {matricula}"
                    ),
                )
            )
            continue

        chaves_vistas.add(chave)
        notas.append(
            Nota(
                matricula=matricula,
                disciplina=disciplina,
                avaliacao=avaliacao,
                nota=valor_nota,
            )
        )

    return notas, erros
