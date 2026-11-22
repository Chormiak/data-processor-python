import logging
import unittest
from pathlib import Path

try:
    from fastapi.testclient import TestClient

    from painel.infra.arquivos import FonteDadosArquivos, FonteDadosMemoria
    from painel.interfaces.api import app, logger, obter_fonte
    from painel.interfaces.config import Settings, obter_settings
except ImportError:  # A API é uma dependência opcional do projeto.
    TestClient = None
    app = None
    obter_fonte = None
    obter_settings = None
    Settings = None
    logger = None
    FonteDadosArquivos = None
    FonteDadosMemoria = None


CONFIG = {
    "media_aprovacao": 6.0,
    "media_recuperacao": 4.0,
    "nota_maxima": 10.0,
}


def fonte_de_teste():
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


@unittest.skipIf(TestClient is None, "FastAPI/httpx não instalados; instale o extra [api]")
class ApiTestCase(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[obter_fonte] = fonte_de_teste
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_metricas(self):
        corpo = self.client.get("/metricas").json()
        self.assertEqual(corpo["alunos_processados"], 2)
        self.assertEqual(corpo["notas_validas"], 3)
        self.assertEqual(corpo["notas_invalidas"], 0)

    def test_obtem_aluno_e_devolve_404_quando_nao_existe(self):
        resposta = self.client.get("/alunos/1")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["nome"], "Ana Lima")

        resposta = self.client.get("/alunos/99")
        self.assertEqual(resposta.status_code, 404)
        self.assertIn("99", resposta.json()["detail"])

    def test_matricula_nao_numerica_devolve_422(self):
        self.assertEqual(self.client.get("/alunos/abc").status_code, 422)

    def test_filtra_notas_por_disciplina_e_matricula(self):
        resposta = self.client.get(
            "/notas",
            params={"disciplina": "matemática", "matricula": 1},
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(resposta.json()), 2)

    def test_relatorio_json_tem_content_type(self):
        resposta = self.client.get("/relatorios/json")
        self.assertTrue(resposta.headers["content-type"].startswith("application/json"))

    def test_formato_de_relatorio_desconhecido_devolve_422(self):
        self.assertEqual(self.client.get("/relatorios/xml").status_code, 422)

    def test_fonte_indisponivel_devolve_503(self):
        app.dependency_overrides[obter_fonte] = lambda: FonteDadosArquivos(
            "arquivo-inexistente-alunos.csv",
            "arquivo-inexistente-notas.csv",
            "arquivo-inexistente-config.json",
        )
        resposta = self.client.get("/metricas")
        self.assertEqual(resposta.status_code, 503)
        self.assertIn("Fonte de dados indisponível", resposta.json()["detail"])

    def test_post_processa_dados_em_memoria(self):
        corpo = {
            "alunos": [{"matricula": 10, "nome": "Caio", "turma": "3A"}],
            "notas": [
                {
                    "matricula": 10,
                    "disciplina": "Português",
                    "avaliacao": "P1",
                    "nota": 8.5,
                }
            ],
            "config": CONFIG,
        }
        resposta = self.client.post("/processar", json=corpo)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["notas_validas"], 1)

    def test_post_separa_regra_de_negocio_de_formato(self):
        corpo = {
            "alunos": [{"matricula": 10, "nome": "Caio", "turma": "3A"}],
            "notas": [
                {
                    "matricula": 10,
                    "disciplina": "Português",
                    "avaliacao": "P1",
                    "nota": 11,
                }
            ],
            "config": CONFIG,
        }
        resposta = self.client.post("/processar", json=corpo)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["notas_invalidas"], 1)

    def test_post_com_formato_incorreto_devolve_422(self):
        resposta = self.client.post("/processar", json={"alunos": "isto nao e uma lista"})
        self.assertEqual(resposta.status_code, 422)

    def test_settings_injetado_configura_nivel_de_log_e_diretorio(self):
        app.dependency_overrides.pop(obter_fonte, None)
        app.dependency_overrides[obter_settings] = lambda: Settings(
            data_dir=Path("/diretorio-inexistente"),
            log_level="WARNING",
        )
        resposta = self.client.get("/metricas")
        self.assertEqual(resposta.status_code, 503)
        self.assertEqual(logger.level, logging.WARNING)


if __name__ == "__main__":
    unittest.main()
