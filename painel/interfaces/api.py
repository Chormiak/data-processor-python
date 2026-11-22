from __future__ import annotations

import logging
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response

from ..core.entidades import Aluno
from ..core.resultados import ResultadoProcessamento
from ..infra.arquivos import FonteDados, FonteDadosArquivos, FonteDadosMemoria
from ..infra.relatorios import criar_gerador
from ..services.processamento import executar_processamento
from .config import Settings, obter_settings
from .schemas import (
    AlunoSchema,
    MetricasSchema,
    NotaSchema,
    ProcessamentoEntrada,
)

logger = logging.getLogger("painel.api")
app = FastAPI(title="Painel de Notas API", version="0.2.0")


def obter_fonte(settings: Settings = Depends(obter_settings)) -> FonteDados:
    logger.setLevel(settings.log_level)
    pasta = settings.data_dir
    return FonteDadosArquivos(
        pasta / "alunos.csv",
        pasta / "notas.csv",
        pasta / "config.json",
    )


def obter_resultado(fonte: FonteDados = Depends(obter_fonte)) -> ResultadoProcessamento:
    return executar_processamento(fonte)


def _aluno_schema(aluno: Aluno, resultado: ResultadoProcessamento) -> dict[str, object]:
    return {
        "matricula": aluno.matricula,
        "nome": aluno.nome,
        "turma": aluno.turma,
        "media": aluno.media(),
        "situacao": aluno.situacao(
            resultado.configuracao.media_aprovacao,
            resultado.configuracao.media_recuperacao,
        ),
    }


def resumir(resultado: ResultadoProcessamento) -> MetricasSchema:
    return MetricasSchema(
        alunos_processados=len(resultado.alunos),
        notas_validas=len(resultado.notas),
        notas_invalidas=resultado.total_notas_invalidas,
        erros_total=resultado.total_erros,
        media_por_disciplina=resultado.medias_disciplinas,
    )


@app.exception_handler(OSError)
async def fonte_indisponivel(request: Request, erro: OSError) -> JSONResponse:
    logger.error("Fonte de dados indisponível em %s: %s", request.url.path, erro)
    return JSONResponse(
        status_code=503,
        content={"detail": f"Fonte de dados indisponível: {erro}"},
    )


@app.get("/alunos", response_model=list[AlunoSchema])
def listar_alunos(
    turma: str | None = None,
    situacao: Literal["aprovado", "recuperação", "reprovado", "sem notas"] | None = None,
    resultado: ResultadoProcessamento = Depends(obter_resultado),
) -> list[dict[str, object]]:
    alunos = resultado.alunos
    if turma is not None:
        alunos = [aluno for aluno in alunos if aluno.turma.casefold() == turma.strip().casefold()]
    if situacao is not None:
        alunos = [
            aluno
            for aluno in alunos
            if aluno.situacao(
                resultado.configuracao.media_aprovacao,
                resultado.configuracao.media_recuperacao,
            )
            == situacao
        ]
    return [_aluno_schema(aluno, resultado) for aluno in alunos]


@app.get("/alunos/{matricula}", response_model=AlunoSchema)
def obter_aluno(
    matricula: int,
    resultado: ResultadoProcessamento = Depends(obter_resultado),
) -> dict[str, object]:
    for aluno in resultado.alunos:
        if aluno.matricula == matricula:
            return _aluno_schema(aluno, resultado)
    raise HTTPException(status_code=404, detail=f"Aluno {matricula} não encontrado")


@app.get("/notas", response_model=list[NotaSchema])
def listar_notas(
    matricula: int | None = None,
    disciplina: str | None = None,
    avaliacao: str | None = None,
    resultado: ResultadoProcessamento = Depends(obter_resultado),
) -> list[dict[str, object]]:
    notas = resultado.notas
    if matricula is not None:
        notas = [nota for nota in notas if nota.matricula == matricula]
    if disciplina is not None:
        notas = [
            nota for nota in notas if nota.disciplina.casefold() == disciplina.strip().casefold()
        ]
    if avaliacao is not None:
        notas = [
            nota for nota in notas if nota.avaliacao.casefold() == avaliacao.strip().casefold()
        ]
    return [
        {
            "matricula": nota.matricula,
            "disciplina": nota.disciplina,
            "avaliacao": nota.avaliacao,
            "nota": nota.nota,
        }
        for nota in notas
    ]


@app.get("/metricas", response_model=MetricasSchema)
def metricas(resultado: ResultadoProcessamento = Depends(obter_resultado)) -> MetricasSchema:
    return resumir(resultado)


@app.get("/relatorios/{formato}")
def relatorio_formatado(
    formato: Literal["texto", "json"],
    resultado: ResultadoProcessamento = Depends(obter_resultado),
) -> Response:
    conteudo = criar_gerador(formato).render(resultado)
    media_type = "text/plain" if formato == "texto" else "application/json"
    return Response(content=conteudo, media_type=media_type)


@app.post("/processar", response_model=MetricasSchema)
def processar(entrada: ProcessamentoEntrada) -> MetricasSchema:
    fonte = FonteDadosMemoria(
        alunos=[aluno.model_dump() for aluno in entrada.alunos],
        notas=[nota.model_dump() for nota in entrada.notas],
        config=entrada.config.model_dump(),
    )
    return resumir(executar_processamento(fonte))
