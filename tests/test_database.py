"""
Tests basicos para funciones de base de datos.
"""

from unittest.mock import patch, MagicMock
import pytest


class TestIntentosFallidos:
    """Tests para control de intentos fallidos"""

    @patch("core.database.supabase")
    def test_registrar_intento_fallido_incrementa(self, mock_supabase):
        """Debe incrementar intentos_fallidos en 1"""
        from core.database import registrar_intento_fallido

        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "intentos_fallidos": 1
        }
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()

        nuevos = registrar_intento_fallido("test@ejemplo.com")

        assert nuevos == 2
        llamada = mock_supabase.table.return_value.update.call_args[0][0]
        assert llamada["intentos_fallidos"] == 2

    @patch("core.database.supabase")
    def test_registrar_intento_fallido_bloquea(self, mock_supabase):
        """Debe setear bloqueado_hasta al llegar a 5 intentos"""
        from core.database import registrar_intento_fallido

        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "intentos_fallidos": 4
        }
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()

        nuevos = registrar_intento_fallido("test@ejemplo.com")

        assert nuevos == 5
        llamada = mock_supabase.table.return_value.update.call_args[0][0]
        assert "bloqueado_hasta" in llamada


class TestResetIntentos:
    """Tests para reiniciar intentos fallidos"""

    @patch("core.database.supabase")
    def test_resetear_intentos(self, mock_supabase):
        """Debe limpiar intentos y bloqueo"""
        from core.database import resetear_intentos

        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()

        resetear_intentos("test@ejemplo.com")

        llamada = mock_supabase.table.return_value.update.call_args[0][0]
        assert llamada["intentos_fallidos"] == 0
        assert llamada["bloqueado_hasta"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
