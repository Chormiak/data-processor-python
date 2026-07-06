import csv

from processador import (
  media_idade,
  extremos_idade,
  contar_por_cidade,
  total_aprovado,
  ranking_gastos_por_cliente,
)


def montar_relatorio(clientes, clientes_invalidos, transacoes, transacoes_invalidas):
  linhas = []
  linhas.append("")

  linhas.append(f"CLIENTES PROCESSADOS ({len(clientes)} válidos)")
  for cliente in clientes:
    linhas.append(
      f"  ID {cliente['id']} | {cliente['nome']} | {cliente['email']} | {cliente['idade']} anos | {cliente['cidade']}"
    )
  linhas.append("")

  linhas.append(f"CLIENTES REJEITADOS ({len(clientes_invalidos)})")
  for item in clientes_invalidos:
    linhas.append(
      f"  ID {item['registro'].get('id', '?')} -"
      + f" {item['registro'].get('nome', '?')}:"
      + f" {', '.join(item['erros'])}"
    )
  linhas.append("")

  linhas.append(f"TRANSAÇÕES PROCESSADAS ({len(transacoes)} válidas)")
  for t in transacoes:
    linhas.append(
      f"  ID {t['id']} | cliente {t['cliente_id']} | "
      f"R$ {t['valor']:.2f} | {t['categoria']} | {t['status']}"
    )
  linhas.append("")

  linhas.append(f"TRANSAÇÕES REJEITADAS ({len(transacoes_invalidas)})")
  for item in transacoes_invalidas:
    linhas.append(
      f"  ID {item['registro'].get('id', '?')} - {', '.join(item['erros'])}"
    )
  linhas.append("")

  media = media_idade(clientes)
  minimo, maximo = extremos_idade(clientes)
  total = total_aprovado(transacoes)

  linhas.append("MÉTRICAS")
  linhas.append(f"  Total aprovado: R$ {total:.2f}")
  if media is not None:
    linhas.append(f"  Média de idade (válidos): {media:.1f}")
  if minimo is not None:
    linhas.append(f"  Faixa de idade: {minimo} – {maximo}")
  linhas.append("")

  linhas.append("CLIENTES POR CIDADE")
  for cidade, qtd in contar_por_cidade(clientes).items():
    sufixo = "cliente" if qtd == 1 else "clientes"
    linhas.append(f"  {cidade}: {qtd} {sufixo}")
  linhas.append("")

  ranking = ranking_gastos_por_cliente(clientes, transacoes)
  if ranking:
    linhas.append("RANKING DE GASTOS (transações aprovadas)")
    for i, (nome, total_gasto) in enumerate(ranking, start=1):
      linhas.append(f"  {i}. {nome} - R$ {total_gasto:.2f}")

  return "\n".join(linhas)


def salvar_relatorio(texto, caminho):
  with open(caminho, "w", encoding="utf-8") as arquivo:
    arquivo.write(texto)


def salvar_clientes_validos(clientes, caminho):
  if not clientes:
    return

  campos = ["id", "nome", "email", "idade", "cidade", "data_cadastro"]
  with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
    escritor = csv.DictWriter(arquivo, fieldnames=campos)
    escritor.writeheader()
    for cliente in clientes:
      escritor.writerow(cliente)
