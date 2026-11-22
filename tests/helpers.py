from painel.infra.arquivos import FonteDadosMemoria

CONFIG = {
    "media_aprovacao": 6.0,
    "media_recuperacao": 4.0,
    "nota_maxima": 10.0,
}


def fonte_minima() -> FonteDadosMemoria:
    return FonteDadosMemoria(
        alunos=[
            {"matricula": "1", "nome": "Ana Lima", "turma": "3A"},
            {"matricula": "2", "nome": "Bia Souza", "turma": "3B"},
        ],
        notas=[
            {"matricula": "1", "disciplina": "Matemática", "avaliacao": "P1", "nota": "6.5"},
            {"matricula": "1", "disciplina": "Matemática", "avaliacao": "P2", "nota": "5.5"},
            {"matricula": "2", "disciplina": "História", "avaliacao": "P1", "nota": "3.5"},
        ],
        config=CONFIG,
    )
