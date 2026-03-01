"""
Tests para el módulo de autenticación (core/auth.py).
"""

import pytest
from core.auth import hashear_pin, verificar_pin


class TestHashearPin:
    """Tests para la función de hasheo de PIN"""

    def test_hashear_pin_genera_hash(self):
        """Debe generar un hash de bcrypt válido"""
        pin = "123456"
        hash_resultado = hashear_pin(pin)
        
        assert hash_resultado is not None
        assert isinstance(hash_resultado, str)
        assert len(hash_resultado) > 0
        assert hash_resultado != pin  # No debe ser el PIN en texto plano

    def test_hashear_pin_diferentes_salts(self):
        """Dos llamadas con el mismo PIN deben generar hashes diferentes (salt único)"""
        pin = "987654"
        hash1 = hashear_pin(pin)
        hash2 = hashear_pin(pin)
        
        assert hash1 != hash2  # bcrypt usa salt aleatorio

    def test_hashear_pin_con_caracteres_especiales(self):
        """Debe manejar PINs con caracteres especiales"""
        pin = "!@#$%^"
        hash_resultado = hashear_pin(pin)
        
        assert hash_resultado is not None
        assert isinstance(hash_resultado, str)


class TestVerificarPin:
    """Tests para la verificación de PIN contra hash"""

    def test_verificar_pin_correcto(self):
        """Debe validar correctamente un PIN correcto"""
        pin = "123456"
        hash_guardado = hashear_pin(pin)
        
        resultado = verificar_pin(pin, hash_guardado)
        
        assert resultado is True

    def test_verificar_pin_incorrecto(self):
        """Debe rechazar un PIN incorrecto"""
        pin_correcto = "123456"
        pin_ingresado = "654321"
        hash_guardado = hashear_pin(pin_correcto)
        
        resultado = verificar_pin(pin_ingresado, hash_guardado)
        
        assert resultado is False

    def test_verificar_pin_vacio(self):
        """Debe rechazar un PIN vacío"""
        hash_guardado = hashear_pin("123456")
        
        resultado = verificar_pin("", hash_guardado)
        
        assert resultado is False

    def test_verificar_pin_case_sensitive(self):
        """Debe ser case-sensitive si el PIN tiene letras"""
        pin = "AbC123"
        hash_guardado = hashear_pin(pin)
        
        assert verificar_pin("AbC123", hash_guardado) is True
        assert verificar_pin("abc123", hash_guardado) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
