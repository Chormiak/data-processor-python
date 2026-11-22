from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AlunoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    matricula: int
    nome: str
    turma: str
    media: float | None
    situacao: str


class NotaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    matricula: int
    disciplina: str
    avaliacao: str
    nota: float


class ErroSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    arquivo: str
    linha: int
    tipo: str
    mensagem: str


class MetricasSchema(BaseModel):
    alunos_processados: int
    notas_validas: int
    notas_invalidas: int
    erros_total: int
    media_por_disciplina: dict[str, float]


class AlunoEntrada(BaseModel):
    matricula: int
    nome: str
    turma: str


class NotaEntrada(BaseModel):
    matricula: int
    disciplina: str
    avaliacao: str
    nota: float


class ConfigEntrada(BaseModel):
    media_aprovacao: float
    media_recuperacao: float
    nota_maxima: float


class ProcessamentoEntrada(BaseModel):
    alunos: list[AlunoEntrada]
    notas: list[NotaEntrada]
    config: ConfigEntrada
