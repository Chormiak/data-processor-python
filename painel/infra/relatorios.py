from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path

from ..core.entidades import Aluno, ErroRegistro
from ..core.resultados import ResultadoProcessamento


class GeradorRelatorio(ABC):
    @abstractmethod
    def render(self, resultado: ResultadoProcessamento) -> str:
        raise NotImplementedError


def _aluno_para_dict(aluno: Aluno, resultado: ResultadoProcessamento) -> dict[str, object]:
    return {
        "matricula": aluno.matricula,
        "nome": aluno.nome,
        "turma": aluno.turma,
        "media": None if aluno.media() is None else round(aluno.media(), 2),
        "situacao": aluno.situacao(
            resultado.configuracao.media_aprovacao,
            resultado.configuracao.media_recuperacao,
        ),
    }


def _erro_para_dict(erro: ErroRegistro) -> dict[str, object]:
    return {
        "arquivo": erro.arquivo,
        "linha": erro.linha,
        "tipo": erro.tipo,
        "mensagem": erro.mensagem,
    }


class GeradorTexto(GeradorRelatorio):
    def render(self, resultado: ResultadoProcessamento) -> str:
        linhas = [
            "PAINEL DE NOTAS — RESUMO",
            f"Alunos processados: {len(resultado.alunos)}",
            (
                f"Registros de nota válidos: {len(resultado.notas)} | "
                f"inválidos: {resultado.total_notas_invalidas}"
            ),
            "",
            "Situação dos alunos",
        ]

        for aluno in sorted(resultado.alunos, key=lambda item: (item.turma, item.nome)):
            media = aluno.media()
            media_formatada = "sem média" if media is None else f"média {media:.2f}"
            situacao = aluno.situacao(
                resultado.configuracao.media_aprovacao,
                resultado.configuracao.media_recuperacao,
            )
            linhas.append(
                f"  {aluno.nome:<24} {aluno.turma:<4} {media_formatada:<14} {situacao}"
            )

        linhas.extend(["", "Média por disciplina"])
        for disciplina, media in sorted(resultado.medias_disciplinas.items()):
            linhas.append(f"  {disciplina:<18} {media:.2f}")

        linhas.extend(["", f"Erros encontrados ({resultado.total_erros})"])
        if resultado.total_erros == 0:
            linhas.append("  Nenhum erro encontrado.")
        else:
            for erro in resultado.erros:
                linhas.append(
                    f"  {erro.arquivo}:{erro.linha} [{erro.tipo}] {erro.mensagem}"
                )

        return "\n".join(linhas) + "\n"


class GeradorJSON(GeradorRelatorio):
    def render(self, resultado: ResultadoProcessamento) -> str:
        documento = {
            "resumo": {
                "alunos_processados": len(resultado.alunos),
                "notas_validas": len(resultado.notas),
                "notas_invalidas": resultado.total_notas_invalidas,
                "erros_total": resultado.total_erros,
            },
            "alunos": [
                _aluno_para_dict(aluno, resultado)
                for aluno in sorted(resultado.alunos, key=lambda item: item.matricula)
            ],
            "media_por_disciplina": {
                disciplina: round(media, 2)
                for disciplina, media in sorted(resultado.medias_disciplinas.items())
            },
            "erros": [_erro_para_dict(erro) for erro in resultado.erros],
        }
        return json.dumps(documento, ensure_ascii=False, indent=2, allow_nan=False)


_GERADORES: dict[str, GeradorRelatorio] = {
    "texto": GeradorTexto(),
    "json": GeradorJSON(),
}


def criar_gerador(formato: str) -> GeradorRelatorio:
    try:
        return _GERADORES[formato]
    except KeyError as erro:
        raise ValueError(f"Formato de relatório não suportado: {formato}") from erro


def salvar_relatorio(
    conteudo: str,
    diretorio: str | Path,
    formato: str,
) -> Path:
    extensao = {"texto": ".txt", "json": ".json"}.get(formato)
    if extensao is None:
        raise ValueError(f"Formato de relatório não suportado: {formato}")

    pasta = Path(diretorio)
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / f"relatorio{extensao}"
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho
