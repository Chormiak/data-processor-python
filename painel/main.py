from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .infra.arquivos import FonteDadosArquivos
from .infra.relatorios import criar_gerador, salvar_relatorio
from .services.processamento import executar_processamento


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="painel",
        description="Consolida notas escolares, registra erros e gera relatórios.",
    )
    parser.add_argument("--alunos", required=True, help="Caminho do CSV de alunos")
    parser.add_argument("--notas", required=True, help="Caminho do CSV de notas")
    parser.add_argument("--config", required=True, help="Caminho do arquivo config.json")
    parser.add_argument(
        "--formato",
        choices=("texto", "json"),
        default="texto",
        help="Formato do relatório (padrão: texto)",
    )
    parser.add_argument("--output", default="output/", help="Diretório de saída")
    parser.add_argument(
        "--log-file",
        default="logs/painel.log",
        help="Arquivo de log (padrão: logs/painel.log)",
    )
    parser.add_argument(
        "--log-level",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        default="INFO",
        help="Nível de log",
    )
    return parser


def configurar_logging(caminho: str | Path, nivel: str) -> None:
    arquivo_log = Path(caminho)
    arquivo_log.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=arquivo_log,
        level=getattr(logging, nivel),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        encoding="utf-8",
        force=True,
    )


def main(argv: list[str] | None = None) -> int:
    argumentos = criar_parser().parse_args(argv)
    configurar_logging(argumentos.log_file, argumentos.log_level)
    logger = logging.getLogger("painel.cli")

    try:
        fonte = FonteDadosArquivos(
            argumentos.alunos,
            argumentos.notas,
            argumentos.config,
        )
        resultado = executar_processamento(fonte)
        conteudo = criar_gerador(argumentos.formato).render(resultado)
        caminho_saida = salvar_relatorio(conteudo, argumentos.output, argumentos.formato)

        logger.info(
            "Processamento concluído: %d alunos, %d notas válidas, %d erros",
            len(resultado.alunos),
            len(resultado.notas),
            resultado.total_erros,
        )
        for erro in resultado.erros:
            logger.warning(
                "%s:%d [%s] %s",
                erro.arquivo,
                erro.linha,
                erro.tipo,
                erro.mensagem,
            )
        print(conteudo, end="")
        print(f"\nRelatório salvo em: {caminho_saida}")
        return 0
    except (OSError, ValueError) as erro:
        logger.exception("Falha ao processar os arquivos")
        print(f"[ERRO] {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
