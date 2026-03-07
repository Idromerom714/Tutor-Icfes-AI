"""
Tests para el módulo de base de datos (core/database.py).
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pytz


class TestObtenerDatosUsuario:
    """Tests para obtener_datos_usuario"""

    @patch("core.database.supabase_admin")
    def test_obtener_usuario_existente(self, mock_supabase_admin):
        """Debe retornar datos del usuario cuando existe"""
        from core.database import obtener_datos_usuario

        mock_data = {
            "id": 1,
            "email": "test@ejemplo.com",
            "nombre": "Test Usuario",
            "plan": "basico",
            "estado": "activo",
            "creditos_totales": 2000,
        }

        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = mock_data

        resultado = obtener_datos_usuario("test@ejemplo.com")

        assert resultado is not None
        assert resultado["email"] == "test@ejemplo.com"
        assert resultado["plan"] == "basico"

    @patch("core.database.supabase_admin")
    def test_obtener_usuario_inexistente(self, mock_supabase_admin):
        """Debe retornar None cuando el usuario no existe"""
        from core.database import obtener_datos_usuario

        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("No data")

        resultado = obtener_datos_usuario("noexiste@ejemplo.com")

        assert resultado is None


class TestDescontarEnergia:
    """Tests para descontar_energia"""

    @patch("core.database.supabase_admin")
    def test_descontar_energia_exitoso(self, mock_supabase_admin):
        """Debe llamar al RPC con los parámetros correctos"""
        from core.database import descontar_energia

        mock_supabase_admin.rpc.return_value.execute.return_value = MagicMock()

        descontar_energia("test@ejemplo.com", 10)

        mock_supabase_admin.rpc.assert_called_once_with(
            "descontar_creditos",
            {"user_email": "test@ejemplo.com", "cantidad": 10}
        )


class TestGuardarOActualizarChat:
    """Tests para guardar_o_actualizar_chat"""

    @patch("core.database.supabase_admin")
    def test_guardar_chat_nuevo(self, mock_supabase_admin):
        """Debe insertar un nuevo chat"""
        from core.database import guardar_o_actualizar_chat

        mock_response = MagicMock()
        mock_response.data = [{"id": 123}]
        mock_supabase_admin.table.return_value.insert.return_value.execute.return_value = mock_response

        mensajes = [
            {"role": "user", "content": "Pregunta"},
            {"role": "assistant", "content": "Respuesta"},
        ]

        resultado = guardar_o_actualizar_chat(
            chat_id=None,
            email="test@ejemplo.com",
            titulo="Test Chat",
            materia="Matemáticas",
            mensajes=mensajes,
            estudiante_id=1
        )

        mock_supabase_admin.table.return_value.insert.assert_called_once()
        assert resultado.data[0]["id"] == 123

    @patch("core.database.supabase_admin")
    def test_actualizar_chat_existente(self, mock_supabase_admin):
        """Debe actualizar un chat existente"""
        from core.database import guardar_o_actualizar_chat

        mock_response = MagicMock()
        mock_supabase_admin.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response

        mensajes = [{"role": "user", "content": "Nueva pregunta"}]

        guardar_o_actualizar_chat(
            chat_id=123,
            email="test@ejemplo.com",
            titulo="Test Chat",
            materia="Matemáticas",
            mensajes=mensajes
        )

        mock_supabase_admin.table.return_value.update.assert_called_once()


class TestIntentosFallidos:
    """Tests para control de intentos fallidos"""

    @patch("core.database.supabase_admin")
    def test_registrar_intento_fallido_incrementa(self, mock_supabase_admin):
        """Debe incrementar intentos_fallidos en 1"""
        from core.database import registrar_intento_fallido

        # Mock del select
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "intentos_fallidos": 2
        }

        # Mock del update
        mock_supabase_admin.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()

        nuevos_intentos = registrar_intento_fallido("test@ejemplo.com")

        assert nuevos_intentos == 3

    @patch("core.database.supabase_admin")
    def test_registrar_intento_fallido_bloquea_a_5(self, mock_supabase_admin):
        """Debe bloquear la cuenta al llegar a 5 intentos"""
        from core.database import registrar_intento_fallido

        # Ya tiene 4 intentos
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "intentos_fallidos": 4
        }

        mock_supabase_admin.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()

        nuevos_intentos = registrar_intento_fallido("test@ejemplo.com")

        assert nuevos_intentos == 5
        
        # Verificar que se llamó update con bloqueado_hasta
        llamada = mock_supabase_admin.table.return_value.update.call_args[0][0]
        assert "bloqueado_hasta" in llamada

    @patch("core.database.supabase_admin")
    def test_resetear_intentos(self, mock_supabase_admin):
        """Debe limpiar intentos y bloqueo"""
        from core.database import resetear_intentos

        mock_supabase_admin.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()

        resetear_intentos("test@ejemplo.com")

        llamada = mock_supabase_admin.table.return_value.update.call_args[0][0]
        assert llamada["intentos_fallidos"] == 0
        assert llamada["bloqueado_hasta"] is None


class TestObtenerEstudiante:
    """Tests para obtener_estudiante"""

    @patch("core.database.supabase_admin")
    def test_obtener_estudiante_existente(self, mock_supabase_admin):
        """Debe retornar datos del estudiante"""
        from core.database import obtener_estudiante

        mock_data = {
            "id": 1,
            "padre_id": 100,
            "nombre": "Juan Estudiante",
            "grado": "11°"
        }

        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.limit.return_value.single.return_value.execute.return_value.data = mock_data

        resultado = obtener_estudiante(100)

        assert resultado is not None
        assert resultado["nombre"] == "Juan Estudiante"

    @patch("core.database.supabase_admin")
    def test_obtener_estudiante_sin_hijos(self, mock_supabase_admin):
        """Debe retornar None si no hay estudiantes"""
        from core.database import obtener_estudiante

        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.limit.return_value.single.return_value.execute.side_effect = Exception("No data")

        resultado = obtener_estudiante(999)

        assert resultado is None


class TestDiagnosticoEstudiante:
    """Tests para persistencia de diagnóstico."""

    @patch("core.database.supabase_admin")
    def test_obtener_ultimo_diagnostico_existente(self, mock_supabase_admin):
        """Debe retornar el último diagnóstico cuando existe."""
        from core.database import obtener_ultimo_diagnostico

        mock_data = [{"estudiante_id": 1, "resultado": {"porcentaje_total": 72.0}}]
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = mock_data

        resultado = obtener_ultimo_diagnostico(1)

        assert resultado is not None
        assert resultado["resultado"]["porcentaje_total"] == 72.0

    @patch("core.database.supabase_admin")
    def test_obtener_ultimo_diagnostico_si_falla_retorna_none(self, mock_supabase_admin):
        """Debe retornar None cuando hay excepción (ej. tabla no existe aún)."""
        from core.database import obtener_ultimo_diagnostico

        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.side_effect = Exception("Table missing")

        resultado = obtener_ultimo_diagnostico(1)

        assert resultado is None

    @patch("core.database.supabase_admin")
    def test_guardar_diagnostico_estudiante(self, mock_supabase_admin):
        """Debe intentar insertar el diagnóstico."""
        from core.database import guardar_diagnostico_estudiante

        mock_supabase_admin.table.return_value.insert.return_value.execute.return_value = MagicMock()

        resultado = guardar_diagnostico_estudiante(
            estudiante_id=1,
            email_padre="test@ejemplo.com",
            resultado={"porcentaje_total": 80.0, "recomendaciones": ["Refuerza Física"]},
        )

        assert resultado is not None
        mock_supabase_admin.table.return_value.insert.assert_called_once()

    @patch("core.database.supabase_admin")
    def test_listar_diagnosticos_estudiante(self, mock_supabase_admin):
        """Debe retornar lista de diagnósticos recientes."""
        from core.database import listar_diagnosticos_estudiante

        mock_data = [
            {"puntaje": 45.0, "creado_el": "2026-03-01T10:00:00+00:00"},
            {"puntaje": 52.0, "creado_el": "2026-03-08T10:00:00+00:00"},
        ]
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = mock_data

        resultado = listar_diagnosticos_estudiante(estudiante_id=1, limite=4)

        assert len(resultado) == 2
        assert resultado[0]["puntaje"] == 45.0

    @patch("core.database.supabase_admin")
    def test_listar_diagnosticos_estudiante_fallback_vacio(self, mock_supabase_admin):
        """Si falla la consulta, debe retornar lista vacía."""
        from core.database import listar_diagnosticos_estudiante

        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.side_effect = Exception("Table missing")

        resultado = listar_diagnosticos_estudiante(estudiante_id=1, limite=4)

        assert resultado == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
