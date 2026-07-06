import os

from leitor import carregar_clientes, carregar_transacoes, carregar_config
from validador import validar_cliente, validar_transacao, separar_registros
from transformador import transformar_clientes, transformar_transacoes
from relatorio import montar_relatorio, salvar_relatorio, salvar_clientes_validos
from logger import limpar_log, registrar_erros

CAMINHO_CLIENTES = "data/clientes.csv"
CAMINHO_TRANSACOES = "data/transacoes.csv"
CAMINHO_CONFIG = "data/config.json"

PASTA_SAIDA = "output"
CAMINHO_RELATORIO = os.path.join(PASTA_SAIDA, "relatorio.txt")
CAMINHO_CLIENTES_VALIDOS = os.path.join(PASTA_SAIDA, "clientes_validos.csv")
CAMINHO_LOG = os.path.join(PASTA_SAIDA, "erros.log")


def main():
  os.makedirs(PASTA_SAIDA, exist_ok=True)
  limpar_log(CAMINHO_LOG)

  print()
  print("=== DataProcessor CLI ===")

  clientes_raw = carregar_clientes(CAMINHO_CLIENTES)
  transacoes_raw = carregar_transacoes(CAMINHO_TRANSACOES)
  config = carregar_config(CAMINHO_CONFIG)

  print()
  print()
  print("[LEITURA]")
  print(f"  clientes.csv ............. {len(clientes_raw)} registros")
  print(f"  transacoes.csv ........... {len(transacoes_raw)} registros")
  print(f"  config.json .............. {'OK' if config else 'FALHOU'}")

  clientes_validos_raw, clientes_invalidos = separar_registros(
    clientes_raw, validar_cliente
  )
  ids_validos = {c["id"] for c in clientes_validos_raw}

  transacoes_validas_raw, transacoes_invalidas = separar_registros(
    transacoes_raw, validar_transacao, ids_clientes=ids_validos, config=config
  )

  print()
  print()
  print("[VALIDAÇÃO]")
  print(f"  Clientes válidos: {len(clientes_validos_raw)} / {len(clientes_raw)}")
  print(f"  Transações válidas: {len(transacoes_validas_raw)} / {len(transacoes_raw)}")

  registrar_erros(clientes_invalidos, CAMINHO_LOG, tipo_registro="cliente")
  registrar_erros(transacoes_invalidas, CAMINHO_LOG, tipo_registro="transacao")

  clientes = transformar_clientes(clientes_validos_raw)
  transacoes = transformar_transacoes(transacoes_validas_raw)

  print()
  print()
  print("[TRANSFORMAÇÃO]")
  print(f"  {len(clientes)} clientes normalizados")
  print(f"  {len(transacoes)} transações normalizadas")

  texto_relatorio = montar_relatorio(
    clientes, clientes_invalidos, transacoes, transacoes_invalidas
  )

  print()
  print()
  print("[RELATÓRIO]")
  print(texto_relatorio)

  salvar_relatorio(texto_relatorio, CAMINHO_RELATORIO)
  salvar_clientes_validos(clientes, CAMINHO_CLIENTES_VALIDOS)

  print()
  print()
  print(f"Relatório salvo em: {CAMINHO_RELATORIO}")
  print(f"Clientes válidos salvos em: {CAMINHO_CLIENTES_VALIDOS}")
  print(f"Log de erros salvo em: {CAMINHO_LOG}")


main()
