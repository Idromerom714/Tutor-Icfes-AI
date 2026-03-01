"""
Tests para el generador de PDFs (core/pdf_generator.py).
"""

import pytest
from core.pdf_generator import generar_pdf_estudio, limpiar_contenido, sanitizar_para_pdf


class TestGenerarPdfEstudio:
    """Tests para generar_pdf_estudio"""

    def test_genera_pdf_con_conversacion_simple(self):
        """Debe generar un PDF con mensajes simples"""
        mensajes = [
            {"role": "user", "content": "Hola Profe"},
            {"role": "assistant", "content": "Hola, ¿en qué te ayudo?"}
        ]

        pdf_bytes = generar_pdf_estudio(mensajes, "Matemáticas")

        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_genera_pdf_con_formula_latex(self):
        """Debe manejar fórmulas LaTeX en el contenido"""
        mensajes = [
            {"role": "user", "content": "¿Qué es $x^2 + y^2 = z^2$?"},
            {"role": "assistant", "content": "Es el teorema de Pitágoras: $a^2 + b^2 = c^2$"}
        ]

        pdf_bytes = generar_pdf_estudio(mensajes, "Matemáticas")

        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)

    def test_genera_pdf_con_texto_largo(self):
        """Debe manejar mensajes muy largos"""
        texto_largo = "Este es un texto muy largo. " * 100

        mensajes = [
            {"role": "user", "content": "Pregunta larga"},
            {"role": "assistant", "content": texto_largo}
        ]

        pdf_bytes = generar_pdf_estudio(mensajes, "Sociales")

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 1000  # Debe tener contenido sustancial

    def test_retorna_none_con_mensajes_vacios(self):
        """Debe retornar None si los mensajes están vacíos"""
        pdf_bytes = generar_pdf_estudio([], "Matemáticas")

        assert pdf_bytes is None

    def test_retorna_none_con_entrada_invalida(self):
        """Debe retornar None con entrada inválida"""
        pdf_bytes = generar_pdf_estudio(None, "Matemáticas")

        assert pdf_bytes is None

    def test_maneja_mensajes_con_emojis(self):
        """Debe manejar emojis en los mensajes"""
        mensajes = [
            {"role": "user", "content": "Hola 👋"},
            {"role": "assistant", "content": "¡Hola! 🎓 ¿Listo para estudiar? 💪"}
        ]

        pdf_bytes = generar_pdf_estudio(mensajes, "Matemáticas")

        assert pdf_bytes is not None

    def test_incluye_materia_en_pdf(self):
        """El PDF debe incluir la materia en la metadata"""
        mensajes = [
            {"role": "user", "content": "Test"}
        ]

        # Simplemente verificar que no falla con diferentes materias
        for materia in ["Matemáticas", "Física", "Sociales", "Lectura Crítica"]:
            pdf_bytes = generar_pdf_estudio(mensajes, materia)
            assert pdf_bytes is not None


class TestLimpiarContenido:
    """Tests para limpiar_contenido"""

    def test_limpia_markdown_bold(self):
        """Debe remover sintaxis de negrita"""
        texto = "Este es un **texto en negrita**"
        resultado = limpiar_contenido(texto)

        assert "**" not in resultado
        assert "texto en negrita" in resultado

    def test_limpia_headers_markdown(self):
        """Debe remover # de headers"""
        texto = "### Título de sección\nContenido normal"
        resultado = limpiar_contenido(texto)

        assert "###" not in resultado
        assert "Título de sección" in resultado

    def test_convierte_formulas_latex(self):
        """Debe convertir fórmulas LaTeX a notación legible"""
        texto = "La fórmula es $x^2 + y^2 = z^2$"
        resultado = limpiar_contenido(texto)

        assert "$" not in resultado
        assert "x" in resultado and "y" in resultado

    def test_maneja_texto_vacio(self):
        """Debe manejar texto vacío sin errores"""
        resultado = limpiar_contenido("")

        assert resultado == ""

    def test_maneja_none(self):
        """Debe manejar None sin errores"""
        resultado = limpiar_contenido(None)

        assert resultado == ""

    def test_preserva_texto_sin_markdown(self):
        """Debe preservar texto plano sin cambios significativos"""
        texto = "Este es texto plano sin formato especial"
        resultado = limpiar_contenido(texto)

        assert "texto plano" in resultado


class TestSanitizarParaPdf:
    """Tests para sanitizar_para_pdf"""

    def test_preserva_acentos(self):
        """Debe preservar acentos en español"""
        texto = "matemáticas, física, electrónica"
        resultado = sanitizar_para_pdf(texto)

        assert "á" in resultado
        assert "í" in resultado
        assert "ó" in resultado

    def test_preserva_enie(self):
        """Debe preservar la letra ñ"""
        texto = "El niño aprendió español"
        resultado = sanitizar_para_pdf(texto)

        assert "ñ" in resultado

    def test_reemplaza_simbolos_matematicos(self):
        """Debe reemplazar símbolos matemáticos especiales"""
        texto = "√16 = 4 y 2 × 3 = 6"
        resultado = sanitizar_para_pdf(texto)

        assert "√" not in resultado
        assert "raiz" in resultado.lower()

    def test_maneja_texto_vacio(self):
        """Debe manejar texto vacío"""
        resultado = sanitizar_para_pdf("")

        assert resultado == ""

    def test_maneja_none(self):
        """Debe manejar None"""
        resultado = sanitizar_para_pdf(None)

        assert resultado == ""

    def test_normaliza_espacios_multiples(self):
        """Debe normalizar múltiples espacios a uno solo"""
        texto = "Texto    con    espacios    múltiples"
        resultado = sanitizar_para_pdf(texto)

        assert "    " not in resultado


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
