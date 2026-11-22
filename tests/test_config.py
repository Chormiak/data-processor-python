import os
import unittest
from pathlib import Path
from unittest.mock import patch

from painel.interfaces.config import obter_settings


class SettingsTestCase(unittest.TestCase):
    def test_le_diretorio_e_nivel_de_log_do_ambiente(self):
        ambiente = {
            "PAINEL_DATA_DIR": "/tmp/dados-alternativos",
            "PAINEL_LOG_LEVEL": "DEBUG",
        }
        with patch.dict(os.environ, ambiente):
            settings = obter_settings()

        self.assertEqual(settings.data_dir, Path("/tmp/dados-alternativos"))
        self.assertEqual(settings.log_level, "DEBUG")

    def test_usa_padroes_quando_variaveis_nao_estao_definidas(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = obter_settings()

        self.assertEqual(settings.data_dir, Path("data"))
        self.assertEqual(settings.log_level, "INFO")


if __name__ == "__main__":
    unittest.main()
