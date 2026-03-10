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


class TestConsumoEnergia:
    """Tests para registrar/listar consumo de energia."""

    @patch("core.database.supabase_admin")
    def test_registrar_consumo_energia(self, mock_supabase_admin):
        """Debe intentar insertar un registro de consumo."""
        from core.database import registrar_consumo_energia

        mock_supabase_admin.table.return_value.insert.return_value.execute.return_value = MagicMock()

        registrar_consumo_energia(
            email_padre="test@ejemplo.com",
            estudiante_id=5,
            cantidad=12,
            materia="Matemáticas",
            metadata={"costo_base": 1},
        )

        llamada = mock_supabase_admin.table.return_value.insert.call_args[0][0]
        assert llamada["email_padre"] == "test@ejemplo.com"
        assert llamada["estudiante_id"] == 5
        assert llamada["cantidad"] == 12

    @patch("core.database.supabase_admin")
    def test_listar_consumo_energia(self, mock_supabase_admin):
        """Debe retornar lista de consumos."""
        from core.database import listar_consumo_energia

        mock_data = [{"email_padre": "test@ejemplo.com", "cantidad": 8}]
        query = mock_supabase_admin.table.return_value.select.return_value.eq.return_value
        query.gte.return_value.lte.return_value.order.return_value.execute.return_value.data = mock_data

        resultado = listar_consumo_energia("test@ejemplo.com", fecha_inicio="2026-03-01", fecha_fin="2026-03-07")

        assert len(resultado) == 1
        assert resultado[0]["cantidad"] == 8

    @patch("core.database.supabase_admin")
    def test_listar_consumo_energia_si_falla_retorna_vacio(self, mock_supabase_admin):
        """Si falla la consulta, debe retornar lista vacia."""
        from core.database import listar_consumo_energia

        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.order.return_value.execute.side_effect = Exception("No table")

        resultado = listar_consumo_energia("test@ejemplo.com")

        assert resultado == []


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


class TestListarChatsUsuario:
    """Tests para listar_chats_usuario"""

    @patch("core.database.supabase_admin")
    def test_listar_chats_sin_filtro_estudiante(self, mock_supabase_admin):
        """Debe listar chats por email sin aplicar filtro de estudiante."""
        from core.database import listar_chats_usuario

        listar_chats_usuario("test@ejemplo.com")

        mock_supabase_admin.table.return_value.select.return_value.eq.assert_called_once_with(
            "email_usuario", "test@ejemplo.com"
        )

    @patch("core.database.supabase_admin")
    def test_listar_chats_con_filtro_estudiante(self, mock_supabase_admin):
        """Debe filtrar por estudiante cuando se envía estudiante_id."""
        from core.database import listar_chats_usuario

        query_mock = mock_supabase_admin.table.return_value.select.return_value.eq.return_value
        query_mock.eq.return_value.order.return_value.execute.return_value = MagicMock()

        listar_chats_usuario("test@ejemplo.com", estudiante_id=55)

        query_mock.eq.assert_called_once_with("estudiante_id", 55)


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


class TestGestionEstudiantes:
    """Tests para listar/crear estudiantes."""

    @patch("core.database.supabase_admin")
    def test_listar_estudiantes(self, mock_supabase_admin):
        """Debe retornar los estudiantes asociados al padre."""
        from core.database import listar_estudiantes

        mock_data = [
            {"id": 1, "padre_id": 100, "nombre": "Ana", "grado": "10°"},
            {"id": 2, "padre_id": 100, "nombre": "Luis", "grado": "11°"},
        ]
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = mock_data

        resultado = listar_estudiantes(100)

        assert len(resultado) == 2
        assert resultado[0]["nombre"] == "Ana"

        # Debe filtrar por activos cuando la columna existe.
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.eq.assert_called_once_with("activo", True)

    @patch("core.database.supabase_admin")
    def test_listar_estudiantes_si_falla_retorna_lista_vacia(self, mock_supabase_admin):
        """Debe retornar [] cuando falla la consulta."""
        from core.database import listar_estudiantes

        mock_supabase_admin.table.return_value.select.return_value.eq.side_effect = Exception("No data")

        resultado = listar_estudiantes(100)

        assert resultado == []

    @patch("core.database.supabase_admin")
    def test_listar_estudiantes_fallback_sin_columna_activo(self, mock_supabase_admin):
        """Si no existe columna activo, debe usar query sin filtro y retornar data."""
        from core.database import listar_estudiantes

        tabla = mock_supabase_admin.table.return_value
        first_eq = tabla.select.return_value.eq.return_value
        first_eq.eq.side_effect = Exception("column activo does not exist")

        fallback_data = [{"id": 9, "padre_id": 100, "nombre": "Sofi", "grado": "10°"}]
        tabla.select.return_value.eq.return_value.order.return_value.execute.return_value.data = fallback_data

        resultado = listar_estudiantes(100)

        assert len(resultado) == 1
        assert resultado[0]["nombre"] == "Sofi"

    @patch("core.database.supabase_admin")
    def test_crear_estudiante(self, mock_supabase_admin):
        """Debe insertar un nuevo estudiante asociado al padre."""
        from core.database import crear_estudiante

        mock_supabase_admin.table.return_value.insert.return_value.execute.return_value = MagicMock()

        crear_estudiante(100, "Maria", "11°")

        llamada = mock_supabase_admin.table.return_value.insert.call_args[0][0]
        assert llamada["padre_id"] == 100
        assert llamada["nombre"] == "Maria"
        assert llamada["grado"] == "11°"

    @patch("core.database.supabase_admin")
    def test_crear_estudiante_con_pin_hash(self, mock_supabase_admin):
        """Debe almacenar pin_hash cuando se envía en la creación."""
        from core.database import crear_estudiante

        mock_supabase_admin.table.return_value.insert.return_value.execute.return_value = MagicMock()

        crear_estudiante(100, "Maria", "11°", pin_hash="hash_demo")

        llamada = mock_supabase_admin.table.return_value.insert.call_args[0][0]
        assert llamada["pin_hash"] == "hash_demo"

    @patch("core.database.supabase_admin")
    def test_renombrar_estudiante(self, mock_supabase_admin):
        """Debe actualizar nombre del estudiante filtrando por padre."""
        from core.database import renombrar_estudiante

        mock_supabase_admin.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock()

        renombrar_estudiante(estudiante_id=5, padre_id=100, nuevo_nombre="Mariana")

        llamada = mock_supabase_admin.table.return_value.update.call_args[0][0]
        assert llamada["nombre"] == "Mariana"

    @patch("core.database.supabase_admin")
    def test_actualizar_pin_estudiante(self, mock_supabase_admin):
        """Debe actualizar el pin hash del estudiante."""
        from core.database import actualizar_pin_estudiante

        mock_supabase_admin.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock()

        actualizar_pin_estudiante(estudiante_id=5, padre_id=100, nuevo_pin_hash="nuevo_hash")

        llamada = mock_supabase_admin.table.return_value.update.call_args[0][0]
        assert llamada["pin_hash"] == "nuevo_hash"

    @patch("core.database.supabase_admin")
    def test_desactivar_estudiante(self, mock_supabase_admin):
        """Debe marcar estudiante como inactivo."""
        from core.database import desactivar_estudiante

        mock_supabase_admin.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock()

        desactivar_estudiante(estudiante_id=5, padre_id=100)

        llamada = mock_supabase_admin.table.return_value.update.call_args[0][0]
        assert llamada["activo"] is False
        assert "desactivado_el" in llamada


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
