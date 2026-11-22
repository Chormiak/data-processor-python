import json
import unittest

from painel.core.entidades import Aluno, Configuracao, Nota
from painel.core.validador import validar_alunos, validar_notas
from painel.infra.relatorios import GeradorJSON, GeradorTexto
from painel.services.processamento import executar_processamento
from tests.helpers import fonte_minima


class ValidacaoAlunosTestCase(unittest.TestCase):
    def test_limpa_espacos_e_aceita_aluno(self):
        alunos, erros = validar_alunos(
            [(2, {"matricula": " 1001 ", "nome": "  Ana Souza  ", "turma": " 3A "})]
        )
        self.assertEqual(erros, [])
        self.assertEqual(len(alunos), 1)
        self.assertEqual(alunos[0].matricula, 1001)
        self.assertEqual(alunos[0].nome, "Ana Souza")
        self.assertEqual(alunos[0].turma, "3A")

    def test_cada_aluno_invalido_gera_um_erro_na_ordem_definida(self):
        alunos, erros = validar_alunos(
            [
                (2, {"matricula": "10", "nome": "Ana", "turma": "3A"}),
                (3, {"matricula": "10", "nome": "Ana repetida", "turma": "3A"}),
                (4, {"matricula": "abc", "nome": "Bruno", "turma": "3B"}),
                (5, {"matricula": "", "nome": "Sem matrícula", "turma": "3B"}),
            ]
        )
        self.assertEqual(len(alunos), 1)
        self.assertEqual(
            [erro.tipo for erro in erros],
            ["matricula_duplicada", "matricula_invalida", "campo_vazio"],
        )
        self.assertEqual([erro.linha for erro in erros], [3, 4, 5])


class ValidacaoNotasTestCase(unittest.TestCase):
    def test_valida_notas_registra_erros_e_preserva_primeira_duplicata(self):
        registros = [
            (2, {"matricula": "1", "disciplina": "Matemática", "avaliacao": "P1", "nota": "8"}),
            (3, {"matricula": "1", "disciplina": "Matemática", "avaliacao": "P1", "nota": "7"}),
            (4, {"matricula": "1", "disciplina": "Física", "avaliacao": "P1", "nota": "oito"}),
            (5, {"matricula": "1", "disciplina": "Física", "avaliacao": "P2", "nota": "11"}),
            (6, {"matricula": "99", "disciplina": "História", "avaliacao": "P1", "nota": "7"}),
            (7, {"matricula": "1", "disciplina": "", "avaliacao": "P1", "nota": "oito"}),
        ]
        notas, erros = validar_notas(registros, {1}, 10.0)
        self.assertEqual(len(notas), 1)
        self.assertEqual(notas[0].nota, 8.0)
        self.assertEqual(
            [erro.tipo for erro in erros],
            [
                "avaliacao_duplicada",
                "nota_invalida",
                "nota_fora_do_intervalo",
                "matricula_inexistente",
                "campo_vazio",
            ],
        )
        self.assertEqual([erro.linha for erro in erros], [3, 4, 5, 6, 7])


class ConfiguracaoTestCase(unittest.TestCase):
    def test_rejeita_limites_nao_finitos(self):
        with self.assertRaisesRegex(ValueError, "devem ser finitas"):
            Configuracao.a_partir_de_dict(
                {
                    "media_aprovacao": float("nan"),
                    "media_recuperacao": 4.0,
                    "nota_maxima": 10.0,
                }
            )


class EntidadeAlunoTestCase(unittest.TestCase):
    def test_media_e_situacao_usam_valor_sem_arredondamento(self):
        aluno = Aluno(
            1,
            "Ana",
            "3A",
            [
                Nota(1, "Matemática", "P1", 5.999),
                Nota(1, "Matemática", "P2", 5.999),
            ],
        )
        self.assertAlmostEqual(aluno.media(), 5.999)
        self.assertEqual(aluno.situacao(6.0, 4.0), "recuperação")
        self.assertEqual(Aluno(2, "Bia", "3B").situacao(6.0, 4.0), "sem notas")


class ProcessamentoERelatoriosTestCase(unittest.TestCase):
    def test_service_consolida_alunos_notas_e_medias(self):
        resultado = executar_processamento(fonte_minima())
        self.assertEqual(len(resultado.alunos), 2)
        self.assertEqual(len(resultado.notas), 3)
        self.assertEqual(resultado.total_erros, 0)
        self.assertEqual(resultado.medias_disciplinas["Matemática"], 6.0)
        self.assertEqual(resultado.alunos[0].situacao(6.0, 4.0), "aprovado")

    def test_relatorio_json_inclui_resumo_alunos_medias_e_erros(self):
        resultado = executar_processamento(fonte_minima())
        documento = json.loads(GeradorJSON().render(resultado))
        self.assertEqual(documento["resumo"]["alunos_processados"], 2)
        self.assertEqual(documento["resumo"]["notas_validas"], 3)
        self.assertEqual(documento["erros"], [])
        self.assertIn("Matemática", documento["media_por_disciplina"])

    def test_relatorio_texto_contem_secoes_obrigatorias(self):
        resultado = executar_processamento(fonte_minima())
        texto = GeradorTexto().render(resultado)
        self.assertIn("PAINEL DE NOTAS — RESUMO", texto)
        self.assertIn("Situação dos alunos", texto)
        self.assertIn("Média por disciplina", texto)
        self.assertIn("Erros encontrados (0)", texto)


if __name__ == "__main__":
    unittest.main()
