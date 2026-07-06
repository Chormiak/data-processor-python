from datetime import datetime


def registrar_erros(invalidos, caminho, tipo_registro="registro"):
  agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  with open(caminho, "a", encoding="utf-8") as arquivo:
    arquivo.write(f"\n=== Execução em {agora} ===\n")
    if not invalidos:
      arquivo.write(f"Nenhum {tipo_registro} inválido encontrado.\n")
      return

    for item in invalidos:
      registro_id = item["registro"].get("id", "?")
      arquivo.write(
        f"[{tipo_registro.upper()} {registro_id}] {', '.join(item['erros'])}\n"
      )


def limpar_log(caminho):
  with open(caminho, "w", encoding="utf-8") as arquivo:
    arquivo.write("=== DataProcessor - log de execução ===\n")
