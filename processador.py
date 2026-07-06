def media_idade(clientes):
  idades_validas = [
    cliente["idade"]
    for cliente in clientes
    if cliente["idade"] and cliente["idade"] > 0
  ]
  if not idades_validas:
    return None
  return sum(idades_validas) / len(idades_validas)


def extremos_idade(clientes):
  idades_validas = [
    cliente["idade"]
    for cliente in clientes
    if cliente["idade"] and cliente["idade"] > 0
  ]
  if not idades_validas:
    return None, None
  return min(idades_validas), max(idades_validas)


def contar_por_cidade(clientes):
  contagem = {}
  for cliente in clientes:
    cidade = cliente["cidade"]
    contagem[cidade] = contagem.get(cidade, 0) + 1
  return contagem


def total_aprovado(transacoes):
  return sum(
    transacao["valor"]
    for transacao in transacoes
    if transacao["status"] == "aprovado"
    and transacao["valor"]
    and transacao["valor"] > 0
  )


def ranking_gastos_por_cliente(clientes, transacoes):
  nomes_por_id = {cliente["id"]: cliente["nome"] for cliente in clientes}

  totais = {}
  for transacao in transacoes:
    if (
      transacao["status"] != "aprovado"
      or not transacao["valor"]
      or transacao["valor"] <= 0
    ):
      continue
    cliente_id = transacao["cliente_id"]
    if cliente_id not in nomes_por_id:
      continue
    nome = nomes_por_id[cliente_id]
    totais[nome] = totais.get(nome, 0) + transacao["valor"]

  return sorted(totais.items(), key=lambda item: item[1], reverse=True)
