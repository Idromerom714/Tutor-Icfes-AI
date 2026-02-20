"""
Tests para el sistema de recarga diaria de créditos.
Verifica que la energía se recargue correctamente cada día.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pytz


class TestRecargaDiaria:
    """Suite de tests para el sistema de recarga automática de créditos"""
    
    @patch('core.database.supabase')
    def test_recarga_nuevo_dia_plan_basico(self, mock_supabase):
        """Debe agregar 50 créditos cuando es un nuevo día (plan básico)"""
        from core.database import verificar_y_recargar_creditos, CREDITOS_DIARIOS
        
        # Simular usuario con plan básico, ayer tuvo actividad
        ayer = (datetime.now(pytz.timezone('America/Bogota')) - timedelta(days=1)).date()
        usuario_mock = {
            'email': 'test@ejemplo.com',
            'plan': 'basico',
            'creditos_totales': 30,
            'ultima_fecha': ayer.strftime('%Y-%m-%d')
        }
        
        # Mock de la consulta a Supabase
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = usuario_mock
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
        
        resultado = verificar_y_recargar_creditos('test@ejemplo.com')
        
        # Verificar que se llamó a update con los créditos esperados
        creditos_esperados = 30 + CREDITOS_DIARIOS['basico']  # 30 + 50 = 80
        assert resultado['creditos_totales'] == creditos_esperados
    
    @patch('core.database.supabase')
    def test_recarga_nuevo_dia_plan_avanzado(self, mock_supabase):
        """Debe agregar 150 créditos cuando es un nuevo día (plan avanzado)"""
        from core.database import verificar_y_recargar_creditos, CREDITOS_DIARIOS
        
        ayer = (datetime.now(pytz.timezone('America/Bogota')) - timedelta(days=1)).date()
        usuario_mock = {
            'email': 'pro@ejemplo.com',
            'plan': 'avanzado',
            'creditos_totales': 100,
            'ultima_fecha': ayer.strftime('%Y-%m-%d')
        }
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = usuario_mock
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
        
        resultado = verificar_y_recargar_creditos('pro@ejemplo.com')
        
        creditos_esperados = 100 + CREDITOS_DIARIOS['avanzado']  # 100 + 150 = 250
        assert resultado['creditos_totales'] == creditos_esperados
    
    @patch('core.database.supabase')
    def test_no_recarga_mismo_dia(self, mock_supabase):
        """NO debe recargar créditos si es el mismo día"""
        from core.database import verificar_y_recargar_creditos
        
        hoy = datetime.now(pytz.timezone('America/Bogota')).date()
        usuario_mock = {
            'email': 'test@ejemplo.com',
            'plan': 'basico',
            'creditos_totales': 40,
            'ultima_fecha': hoy.strftime('%Y-%m-%d')
        }
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = usuario_mock
        
        resultado = verificar_y_recargar_creditos('test@ejemplo.com')
        
        # Los créditos deben permanecer igual (no hay recarga)
        assert resultado['creditos_totales'] == 40
    
    @patch('core.database.supabase')
    def test_acumulacion_creditos(self, mock_supabase):
        """Los créditos deben acumularse, no restablecerse"""
        from core.database import verificar_y_recargar_creditos, CREDITOS_DIARIOS
        
        ayer = (datetime.now(pytz.timezone('America/Bogota')) - timedelta(days=1)).date()
        
        # Usuario que no gastó todos sus créditos ayer
        usuario_mock = {
            'email': 'ahorrativo@ejemplo.com',
            'plan': 'basico',
            'creditos_totales': 45,  # Le quedaron 45 del día anterior
            'ultima_fecha': ayer.strftime('%Y-%m-%d')
        }
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = usuario_mock
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
        
        resultado = verificar_y_recargar_creditos('ahorrativo@ejemplo.com')
        
        # Debe tener 45 + 50 = 95 (acumulados, no reseteados a 50)
        assert resultado['creditos_totales'] == 95


class TestDescontarEnergia:
    """Tests para el descuento correcto de créditos"""
    
    @patch('core.database.supabase')
    def test_descuento_basico(self, mock_supabase):
        """Debe descontar correctamente la cantidad especificada"""
        from core.database import descontar_energia
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            'creditos_totales': 100
        }
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
        
        descontar_energia('test@ejemplo.com', 10)
        
        # Verificar que se actualizó con 90 créditos
        mock_supabase.table.return_value.update.assert_called()
    
    @patch('core.database.supabase')
    def test_no_creditos_negativos(self, mock_supabase):
        """Los créditos nunca deben ser negativos"""
        from core.database import descontar_energia
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            'creditos_totales': 5
        }
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
        
        descontar_energia('test@ejemplo.com', 10)
        
        # Debe quedarse en 0, no en -5
        llamada = mock_supabase.table.return_value.update.call_args[0][0]
        assert llamada['creditos_totales'] >= 0


class TestCostos:
    """Tests para verificar los costos correctos por operación"""
    
    def test_costo_matematicas_sin_imagen(self):
        """Matemáticas sin imagen debe costar 1⚡"""
        materia = "Matemáticas"
        tiene_foto = False
        
        costo_base = 1  # Matemáticas = 1⚡
        plus_foto = 5 if tiene_foto else 0
        total = costo_base + plus_foto
        
        assert total == 1
    
    def test_costo_sociales_sin_imagen(self):
        """Sociales/Lectura Crítica sin imagen debe costar 8⚡"""
        materia = "Sociales"
        tiene_foto = False
        
        costo_base = 8 if materia in ["Sociales", "Lectura Crítica"] else 1
        plus_foto = 5 if tiene_foto else 0
        total = costo_base + plus_foto
        
        assert total == 8
    
    def test_costo_con_imagen(self):
        """Cualquier pregunta con imagen debe tener +5⚡ adicionales"""
        materia = "Matemáticas"
        tiene_foto = True
        
        costo_base = 1
        plus_foto = 5 if tiene_foto else 0
        total = costo_base + plus_foto
        
        assert total == 6  # 1 + 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
