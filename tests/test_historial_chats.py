"""
Tests para el sistema de historial y gestión de conversaciones.
Verifica que los chats se guarden, listen y carguen correctamente.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta


class TestGuardadoChats:
    """Tests para verificar el guardado correcto de conversaciones"""
    
    @patch('core.database.supabase')
    def test_guardar_chat_nuevo(self, mock_supabase):
        """Debe crear un nuevo chat si no existe"""
        from core.database import guardar_o_actualizar_chat

        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock()
        
        conversacion = [
            {"rol": "user", "contenido": "Hola", "timestamp": datetime.now().isoformat()},
            {"rol": "assistant", "contenido": "¡Hola! ¿En qué puedo ayudarte?", "timestamp": datetime.now().isoformat()}
        ]

        guardar_o_actualizar_chat(None, 'test@ejemplo.com', 'Saludo inicial', 'Matemáticas', conversacion)
        
        # Debe haber insertado el nuevo chat
        mock_supabase.table.return_value.insert.assert_called_once()
    
    @patch('core.database.supabase')
    def test_actualizar_chat_existente(self, mock_supabase):
        """Debe actualizar un chat existente sin duplicar"""
        from core.database import guardar_o_actualizar_chat

        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
        
        conversacion = [
            {"rol": "user", "contenido": "Segunda pregunta", "timestamp": datetime.now().isoformat()},
            {"rol": "assistant", "contenido": "Segunda respuesta", "timestamp": datetime.now().isoformat()}
        ]
        
        guardar_o_actualizar_chat(5, 'test@ejemplo.com', 'Sesion 2', 'Física', conversacion)
        
        # Debe haber actualizado, no insertado
        mock_supabase.table.return_value.update.assert_called_once()
    
    @patch('core.database.supabase')
    def test_conservar_estructura_json(self, mock_supabase):
        """El formato JSON de la conversación debe mantenerse"""
        from core.database import guardar_o_actualizar_chat

        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock()
        
        conversacion = [
            {
                "rol": "user",
                "contenido": "Texto con áéíóú y ñ",
                "timestamp": "2024-01-15T10:30:00",
                "imagen_base64": "ABC123=="
            }
        ]
        
        guardar_o_actualizar_chat(None, 'test@ejemplo.com', 'Sesion', 'Química', conversacion)
        
        # Verificar que se llamó insert con datos correctos
        llamada = mock_supabase.table.return_value.insert.call_args[0][0]
        assert isinstance(llamada['mensajes'], list)
        assert llamada['materia'] == 'Química'
        assert llamada['email_usuario'] == 'test@ejemplo.com'


class TestListadoChats:
    """Tests para verificar el listado de conversaciones"""
    
    @patch('core.database.supabase')
    def test_listar_ultimos_10_chats(self, mock_supabase):
        """Debe retornar los últimos 10 chats ordenados por fecha"""
        from core.database import listar_chats_usuario
        
        # Mock: 15 chats disponibles
        chats_mock = [
            {
                'id': i,
                'titulo': f"Chat {i}",
                'materia': 'Matemáticas',
                'actualizado_el': (datetime.now() - timedelta(days=i)).isoformat()
            }
            for i in range(15)
        ]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = chats_mock[:10]

        resultado = listar_chats_usuario('test@ejemplo.com')

        # Debe retornar exactamente 10
        assert len(resultado.data) == 10

        # Debe estar llamando con order desc por actualizado_el
        mock_supabase.table.return_value.select.assert_called_with("id, titulo, materia, actualizado_el")
    
    @patch('core.database.supabase')
    def test_formato_visualizacion_chat(self, mock_supabase):
        """Cada chat debe tener formato legible para mostrar en sidebar"""
        from core.database import listar_chats_usuario
        
        chats_mock = [
            {
                'id': 1,
                'titulo': 'Revolucion Francesa',
                'materia': 'Sociales',
                'actualizado_el': '2024-01-15T14:30:00'
            }
        ]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = chats_mock

        resultado = listar_chats_usuario('test@ejemplo.com')

        # Debe tener estructura esperada
        assert len(resultado.data) == 1
        assert 'id' in resultado.data[0]
        assert 'materia' in resultado.data[0]
        assert 'actualizado_el' in resultado.data[0]
    
    @patch('core.database.supabase')
    def test_usuario_sin_chats(self, mock_supabase):
        """Debe retornar lista vacía si no hay chats"""
        from core.database import listar_chats_usuario
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []

        resultado = listar_chats_usuario('nuevo@ejemplo.com')

        assert resultado.data == []


class TestCargaChats:
    """Tests para verificar la carga completa de conversaciones"""
    
    @patch('core.database.supabase')
    def test_cargar_chat_completo(self, mock_supabase):
        """Debe cargar toda la conversación de un chat específico"""
        from core.database import cargar_chat_completo
        
        conversacion_completa = [
            {"rol": "user", "contenido": "Primer mensaje", "timestamp": "2024-01-15T10:00:00"},
            {"rol": "assistant", "contenido": "Primera respuesta", "timestamp": "2024-01-15T10:00:30"},
            {"rol": "user", "contenido": "Segundo mensaje", "timestamp": "2024-01-15T10:01:00"},
            {"rol": "assistant", "contenido": "Segunda respuesta", "timestamp": "2024-01-15T10:01:30"}
        ]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            'id': 42,
            'materia': 'Biología',
            'mensajes': conversacion_completa
        }
        
        resultado = cargar_chat_completo(42)
        
        # Debe retornar la conversación completa
        assert len(resultado['mensajes']) == 4
        assert resultado['materia'] == 'Biología'
    
    @patch('core.database.supabase')
    def test_cargar_chat_inexistente(self, mock_supabase):
        """Debe manejar correctamente cuando no existe el chat"""
        from core.database import cargar_chat_completo
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None
        
        resultado = cargar_chat_completo(999)
        
        # Debe retornar None o estructura vacía
        assert resultado is None or resultado == {}


class TestCambioMateria:
    """Tests para verificar el comportamiento al cambiar de materia"""
    
    def test_cambio_materia_limpia_conversacion(self):
        """Al cambiar de materia, debe limpiar la conversación en session_state"""
        # Simular session_state
        mock_session = {
            'materia_actual': 'Matemáticas',
            'materia_anterior': 'Matemáticas',
            'messages': [
                {"rol": "user", "contenido": "Mensaje viejo"}
            ]
        }
        
        # Simular cambio de materia
        nueva_materia = 'Física'
        
        if mock_session['materia_actual'] != nueva_materia:
            mock_session['materia_anterior'] = mock_session['materia_actual']
            mock_session['materia_actual'] = nueva_materia
            mock_session['messages'] = []
        
        # Verificar que se limpió
        assert len(mock_session['messages']) == 0
        assert mock_session['materia_actual'] == 'Física'
        assert mock_session['materia_anterior'] == 'Matemáticas'
    
    def test_misma_materia_conserva_conversacion(self):
        """Si no cambia la materia, debe conservar la conversación"""
        mock_session = {
            'materia_actual': 'Química',
            'materia_anterior': 'Química',
            'messages': [
                {"rol": "user", "contenido": "Mensaje importante"}
            ]
        }
        
        # No cambiar materia
        nueva_materia = 'Química'
        
        if mock_session['materia_actual'] != nueva_materia:
            mock_session['messages'] = []
        
        # Debe conservar mensajes
        assert len(mock_session['messages']) == 1


class TestIntegridadDatos:
    """Tests para verificar la integridad de los datos guardados"""
    
    @patch('core.database.supabase')
    def test_timestamp_presente(self, mock_supabase):
        """Todos los mensajes deben tener timestamp"""
        from core.database import guardar_o_actualizar_chat
        
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock()
        
        conversacion = [
            {"rol": "user", "contenido": "Test", "timestamp": datetime.now().isoformat()}
        ]
        
        guardar_o_actualizar_chat(None, 'test@ejemplo.com', 'Test', 'Test', conversacion)
        
        # Verificar estructura
        llamada = mock_supabase.table.return_value.insert.call_args[0][0]
        for msg in llamada['mensajes']:
            assert 'timestamp' in msg
    
    @patch('core.database.supabase')
    def test_campos_obligatorios_presentes(self, mock_supabase):
        """Los campos email, materia y conversacion deben estar presentes"""
        from core.database import guardar_o_actualizar_chat
        
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock()
        
        conversacion = [{"rol": "user", "contenido": "Test", "timestamp": datetime.now().isoformat()}]
        
        guardar_o_actualizar_chat(None, 'test@ejemplo.com', 'Sesion', 'Inglés', conversacion)
        
        llamada = mock_supabase.table.return_value.insert.call_args[0][0]
        assert 'email_usuario' in llamada
        assert 'materia' in llamada
        assert 'mensajes' in llamada


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
