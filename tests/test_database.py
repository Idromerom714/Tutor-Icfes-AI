import pytest
from core.database import verificar_acceso

def test_limite_creditos_basico():
    # Simulamos un usuario con el plan básico que ya gastó sus 10 preguntas
    usuario_gastado = {
        "plan": "basico",
        "preguntas_usadas": 10,
        "ultima_fecha": "2026-02-14"
    }
    
    # El sistema debería negar el acceso
    puede_preguntar = verificar_acceso(usuario_gastado, es_imagen=False)
    assert puede_preguntar is False

def test_limite_creditos_avanzado():
    # Usuario avanzado que lleva 49 de 50 preguntas
    usuario_pro = {
        "plan": "avanzado",
        "preguntas_usadas": 49,
        "ultima_fecha": "2026-02-14"
    }
    
    # Aún debería poder hacer una pregunta más
    puede_preguntar = verificar_acceso(usuario_pro, es_imagen=False)
    assert puede_preguntar is True