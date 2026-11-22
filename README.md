# Painel de Notas da Turma

Aplicação Python para consolidar notas escolares exportadas em CSV. O programa valida cada registro, acumula erros com o arquivo e a linha de origem, calcula médias e situação dos alunos e gera relatórios em texto ou JSON.

O projeto foi organizado em camadas: regras de negócio em `core/`, leitura e escrita em `infra/`, orquestração em `services/` e interfaces em `main.py` (CLI) e `interfaces/api.py` (API opcional).

## Requisitos

- Python 3.10 ou superior.
- A execução pela CLI e os testes do núcleo usam somente a biblioteca padrão.
- A API REST é opcional e utiliza FastAPI, Uvicorn, Pydantic e HTTPX.

## Estrutura

```text
painel-notas-turma/
├── painel/
│   ├── __main__.py
│   ├── main.py
│   ├── core/
│   │   ├── entidades.py
│   │   ├── metricas.py
│   │   ├── resultados.py
│   │   └── validador.py
│   ├── infra/
│   │   ├── arquivos.py
│   │   ├── relatorios.py
│   │   └── tipos.py
│   ├── interfaces/
│   │   ├── api.py
│   │   ├── config.py
│   │   └── schemas.py
│   └── services/
│       └── processamento.py
├── data/
│   ├── alunos.csv
│   ├── notas.csv
│   └── config.json
├── tests/
├── logs/
├── output/
└── pyproject.toml
```

## Formato dos dados

`alunos.csv`:

```csv
matricula,nome,turma
1001,Ana Souza,3A
1002,Bruno Lima,3A
```

`notas.csv`:

```csv
matricula,disciplina,avaliacao,nota
1001,Matemática,P1,8.5
1001,Matemática,P2,7.0
```

`config.json`:

```json
{
  "media_aprovacao": 6.0,
  "media_recuperacao": 4.0,
  "nota_maxima": 10.0
}
```

Os arquivos incluídos em `data/` são uma base demonstrativa criada para este repositório. Ela contém 32 alunos válidos, 457 notas válidas, 27 notas rejeitadas e 30 erros no total, de acordo com os números de conferência da especificação. Para processar os arquivos originais da atividade, substitua os três arquivos mantendo os cabeçalhos e os campos acima.

## Execução pela CLI

Na raiz do projeto:

```bash
python -m painel \
  --alunos data/alunos.csv \
  --notas data/notas.csv \
  --config data/config.json \
  --formato json \
  --output output/
```

Para gerar relatório em texto, use `--formato texto`. O relatório é salvo como `output/relatorio.json` ou `output/relatorio.txt` e também é exibido no terminal. O diretório de saída é criado automaticamente.

O log é gravado em `logs/painel.log`. É possível alterar o arquivo e o nível de log:

```bash
python -m painel --alunos data/alunos.csv --notas data/notas.csv \
  --config data/config.json --formato texto --output output/ \
  --log-file logs/painel.log --log-level DEBUG
```

## Regras de validação

Os campos obrigatórios vazios são rejeitados. Espaços no início ou no fim são removidos antes da validação. Em `alunos.csv`, o programa rejeita matrícula não numérica e matrícula duplicada. Em `notas.csv`, rejeita nota não numérica, nota fora do intervalo `0..nota_maxima`, matrícula que não pertence aos alunos válidos e avaliação duplicada para a combinação matrícula/disciplina/avaliação.

A validação segue a ordem definida na atividade: um registro inválido gera apenas o primeiro erro encontrado. Em duplicatas, o primeiro registro válido permanece. Erros usam numeração de linha com cabeçalho na linha 1. Nenhuma linha inválida interrompe o restante do processamento.

A situação do aluno é calculada pela média sem arredondamento:

- média maior ou igual a `media_aprovacao`: `aprovado`;
- média maior ou igual a `media_recuperacao`: `recuperação`;
- abaixo disso: `reprovado`;
- aluno sem notas válidas: `sem notas`.

O arredondamento para duas casas acontece somente na apresentação dos relatórios.

## Testes

Execute a suíte com:

```bash
python -m unittest discover -s tests -v
```

Os testes de `core`, `service` e relatórios usam dados em memória, sem depender dos CSVs da pasta `data/`.

## API REST opcional (aulas 21–25)

Instale o extra da API:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[api]"
```

Inicie o servidor na raiz do projeto:

```bash
uvicorn painel.interfaces.api:app --reload
```

Documentação interativa: <http://127.0.0.1:8000/docs>.

Rotas disponíveis:

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/alunos` | Lista alunos; aceita `?turma=3A` e `?situacao=aprovado` |
| `GET` | `/alunos/{matricula}` | Consulta aluno; devolve `404` se não existir |
| `GET` | `/notas` | Lista notas; aceita filtros `matricula`, `disciplina` e `avaliacao` |
| `GET` | `/metricas` | Retorna totais e médias por disciplina |
| `GET` | `/relatorios/{formato}` | Retorna relatório `texto` ou `json` com o `Content-Type` correto |
| `POST` | `/processar` | Processa alunos, notas e configuração enviados no corpo JSON |

A API usa `Depends` para injetar a fonte e o resultado do processamento. Erros de acesso aos arquivos (`OSError`) são convertidos em `503`; recurso inexistente retorna `404`; parâmetros ou corpos com formato inválido retornam `422`.

O caminho dos dados e o nível de log são configuráveis pelo ambiente:

```bash
PAINEL_DATA_DIR=/srv/dados PAINEL_LOG_LEVEL=DEBUG \
  uvicorn painel.interfaces.api:app
```

`PAINEL_DATA_DIR` deve conter `alunos.csv`, `notas.csv` e `config.json`. Sem a variável, a API usa `data/`. Os testes da API substituem a dependência de fonte com `dependency_overrides` e usam `TestClient`, sem subir servidor.

Sem o extra `[api]`, os testes de API são marcados como ignorados e os testes do núcleo continuam executando.
