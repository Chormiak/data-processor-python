from datetime import date


def email_valido(email):
  if not email or not email.strip():
    return False
  if "@" not in email:
    return False
  partes = email.strip().split("@")
  if len(partes) != 2 or "." not in partes[1]:
    return False
  return True


def idade_valida(idade):
  if idade is None:
    return False
  return 0 < idade < 120


def data_valida(texto):
  if not texto:
    return False
  try:
    date.fromisoformat(texto)
    return True
  except ValueError:
    return False


def valor_valido(valor, minimo=0):
  if valor is None:
    return False
  return valor > minimo


def categoria_valida(categoria, categorias_permitidas):
  return categoria in categorias_permitidas


def validar_cliente(cliente):
  erros = []

  if cliente.get("id") is None:
    erros.append("id inválido")

  if not cliente.get("nome", "").strip():
    erros.append("nome vazio")

  if not email_valido(cliente.get("email")):
    erros.append(f"email inválido: '{cliente.get('email')}'")

  if not idade_valida(cliente.get("idade")):
    erros.append(f"idade inválida: {cliente.get('idade')}")

  if not data_valida(cliente.get("data_cadastro")):
    erros.append(f"data inválida: '{cliente.get('data_cadastro')}'")

  return erros


def validar_transacao(transacao, ids_clientes, config):
  erros = []

  if transacao.get("id") is None:
    erros.append("id inválido")

  if transacao.get("cliente_id") not in ids_clientes:
    erros.append(f"cliente_id inexistente: {transacao.get('cliente_id')}")

  valor_minimo = config.get("valor_minimo", 0)
  if not valor_valido(transacao.get("valor"), minimo=valor_minimo):
    erros.append(f"valor inválido: {transacao.get('valor')}")

  categorias = config.get("categorias_validas", [])
  if not categoria_valida(transacao.get("categoria", ""), categorias):
    erros.append(f"categoria inválida: '{transacao.get('categoria')}'")

  status_validos = config.get("status_validos", [])
  if transacao.get("status") not in status_validos:
    erros.append(f"status inválido: '{transacao.get('status')}'")

  return erros


def separar_registros(registros, funcao_validar, **kwargs):
  validos = []
  invalidos = []
  for registro in registros:
    erros = funcao_validar(registro, **kwargs)
    if erros:
      invalidos.append({"registro": registro, "erros": erros})
    else:
      validos.append(registro)
  return validos, invalidos
