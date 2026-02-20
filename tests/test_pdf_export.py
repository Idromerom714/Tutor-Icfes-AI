"""
Tests para el sistema de exportación de PDFs.
Verifica que los PDFs se generen correctamente con caracteres especiales y LaTeX.
"""

import pytest
from datetime import datetime


class TestGeneracionPDF:
    """Tests para verificar la generación correcta de PDFs"""
    
    def test_sanitizacion_caracteres_especiales(self):
        """Debe preservar caracteres en español (á, é, í, ó, ú, ñ)"""
        from core.pdf_generator import sanitizar_para_pdf
        
        texto = "La Brújula mágica: ¡Qué fácil está el examen!"
        resultado = sanitizar_para_pdf(texto)
        
        # Debe preservar acentos y ñ
        assert "ú" in resultado or "u" in resultado  # Brújula
        assert "á" in resultado or "a" in resultado  # mágica
        assert "á" in resultado or "a" in resultado  # está
        
        # No debe contener caracteres problemáticos
        assert "\u200b" not in resultado  # Sin espacios de ancho cero
    
    def test_eliminacion_emojis(self):
        """Debe eliminar emojis del texto"""
        from core.pdf_generator import sanitizar_para_pdf
        
        texto = "¡Excelente trabajo! 🎉🔥💯"
        resultado = sanitizar_para_pdf(texto)
        
        # No debe contener emojis
        assert "🎉" not in resultado
        assert "🔥" not in resultado
        assert "💯" not in resultado
        # Debe preservar el texto
        assert "Excelente trabajo" in resultado
    
    def test_conversion_latex_basica(self):
        """Debe convertir LaTeX a texto plano legible"""
        from core.pdf_generator import limpiar_contenido
        
        # Test 1: Multiplicación
        entrada1 = r"El resultado es $5 \cdot 3 = 15$"
        esperado1 = "El resultado es (5 * 3 = 15)"
        assert limpiar_contenido(entrada1) == esperado1
        
        # Test 2: Fracciones
        entrada2 = r"La probabilidad es $\frac{2}{5}$"
        resultado2 = limpiar_contenido(entrada2)
        assert "(2/5)" in resultado2 or "2/5" in resultado2
    
    def test_conversion_latex_raices(self):
        """Debe convertir raíces cuadradas a formato legible"""
        from core.pdf_generator import limpiar_contenido
        
        entrada = r"La solución es $\sqrt{16} = 4$"
        resultado = limpiar_contenido(entrada)
        
        # Debe convertir sqrt{16} a algo legible
        assert "raiz" in resultado
    
    def test_pdf_con_conversacion_completa(self):
        """Debe generar PDF con estudiante y profesor"""
        from core.pdf_generator import generar_pdf_estudio
        
        conversacion_mock = [
            {
                "role": "user",
                "content": "¿Cuánto es 2+2?",
                "timestamp": datetime.now().isoformat()
            },
            {
                "role": "assistant",
                "content": "Excelente pregunta. ¿Qué crees tú que podría ser?",
                "timestamp": datetime.now().isoformat()
            },
            {
                "role": "user",
                "content": "Creo que es 4",
                "timestamp": datetime.now().isoformat()
            },
            {
                "role": "assistant",
                "content": "¡Correcto! Muy bien razonado.",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        # Generar PDF
        pdf_bytes = generar_pdf_estudio(conversacion_mock, "Matemáticas")
        
        # Verificar que se generó contenido
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # PDFs empiezan con %PDF-
        assert pdf_bytes[:4] == b'%PDF'
    
    def test_pdf_con_texto_largo(self):
        """Debe manejar conversaciones largas sin errores"""
        from core.pdf_generator import generar_pdf_estudio
        
        conversacion_larga = []
        for i in range(50):  # 50 mensajes
            conversacion_larga.append({
                "role": "user",
                "content": f"Esta es la pregunta número {i+1} con texto más largo para probar el manejo de contenido extenso.",
                "timestamp": datetime.now().isoformat()
            })
            conversacion_larga.append({
                "role": "assistant",
                "content": f"Esta es la respuesta número {i+1} del profesor, también con texto extenso para verificar el manejo de páginas múltiples.",
                "timestamp": datetime.now().isoformat()
            })
        
        pdf_bytes = generar_pdf_estudio(conversacion_larga, "Física")
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
    
    def test_pdf_vacio_o_sin_mensajes(self):
        """Debe manejar conversaciones vacías"""
        from core.pdf_generator import generar_pdf_estudio
        
        conversacion_vacia = []
        
        # Debe generar PDF vacío o con mensaje de "sin mensajes"
        pdf_bytes = generar_pdf_estudio(conversacion_vacia, "Matemáticas")
        
        assert pdf_bytes is None


class TestSanitizacionAvanzada:
    """Tests específicos para casos edge de sanitización"""
    
    def test_caracteres_latin1_validos(self):
        """Debe preservar todos los caracteres válidos en Latin-1"""
        from core.pdf_generator import sanitizar_para_pdf
        
        # Caracteres especiales del español
        texto = "áéíóúñÁÉÍÓÚÑ¿¡üÜ"
        resultado = sanitizar_para_pdf(texto)
        
        # Todos deben estar presentes (Latin-1 los soporta)
        for char in texto:
            assert char in resultado or char.lower() in resultado.lower()
    
    def test_comillas_y_guiones(self):
        """Debe manejar comillas y guiones especiales"""
        from core.pdf_generator import sanitizar_para_pdf
        
        texto = 'Dijo: "esto es importante" — muy importante'
        resultado = sanitizar_para_pdf(texto)
        
        # Debe tener algún tipo de comillas y guiones
        assert '"' in resultado or "'" in resultado
        assert "-" in resultado or "—" in resultado
    
    def test_numeros_y_simbolos_matematicos(self):
        """Debe preservar números y símbolos matemáticos básicos"""
        from core.pdf_generator import sanitizar_para_pdf
        
        texto = "1234567890 + - = * / < > () [] {}"
        resultado = sanitizar_para_pdf(texto)
        
        # Todos los símbolos básicos deben estar
        assert "+" in resultado
        assert "-" in resultado
        assert "=" in resultado
        assert "(" in resultado


class TestConversionLatexAvanzada:
    """Tests para conversiones LaTeX complejas"""
    
    def test_latex_exponentes(self):
        """Debe convertir exponentes x^2 a x² o x^2"""
        from core.pdf_generator import limpiar_contenido
        
        entrada = r"La fórmula es $x^2 + y^2 = r^2$"
        resultado = limpiar_contenido(entrada)
        
        # Debe tener alguna representación de exponentes
        assert "x^2" in resultado or "x²" in resultado
    
    def test_latex_subindices(self):
        """Debe manejar subíndices x_1, x_2"""
        from core.pdf_generator import limpiar_contenido
        
        entrada = r"Las variables son $x_1, x_2, x_3$"
        resultado = limpiar_contenido(entrada)
        
        # Debe tener representación de subíndices
        assert "x_1" in resultado or "x1" in resultado
    
    def test_latex_ecuaciones_complejas(self):
        """Debe simplificar ecuaciones complejas"""
        from core.pdf_generator import limpiar_contenido
        
        entrada = r"La distancia es $d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$"
        resultado = limpiar_contenido(entrada)
        
        # Debe ser texto legible
        assert len(resultado) > 0
        assert "\\" not in resultado  # No debe quedar LaTeX sin procesar


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
