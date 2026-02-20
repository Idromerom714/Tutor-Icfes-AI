"""
Tests para el motor de IA y seleccion de modelos.
Verifica que se elija el modelo correcto segun materia e imagen.
"""

import pytest
from unittest.mock import patch


class TestSeleccionModelo:
    """Tests para la logica de seleccion de modelos"""

    @patch("core.ai_engine.requests.post")
    def test_matematicas_sin_imagen_usa_deepseek(self, mock_post):
        """Matematicas sin imagen debe usar DeepSeek"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Respuesta de prueba"}}]
        }

        llamar_profe_saber(
            mensaje_usuario="Cuanto es 2+2?",
            contexto_pdf="",
            imagen_bytes=None,
            materia="Matematicas",
            historial_mensajes=[],
        )

        body = mock_post.call_args[1]["json"]
        assert "deepseek" in body["model"].lower()

    @patch("core.ai_engine.requests.post")
    def test_matematicas_con_imagen_usa_grok(self, mock_post):
        """Matematicas con imagen debe usar Grok"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Respuesta con vision"}}]
        }

        llamar_profe_saber(
            mensaje_usuario="Resuelve este ejercicio",
            contexto_pdf="",
            imagen_bytes=b"fake_image_data",
            materia="Matematicas",
            historial_mensajes=[],
        )

        body = mock_post.call_args[1]["json"]
        assert "grok" in body["model"].lower()

    @patch("core.ai_engine.requests.post")
    def test_sociales_usa_grok(self, mock_post):
        """Sociales debe usar Grok"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Analisis social"}}]
        }

        llamar_profe_saber(
            mensaje_usuario="Que fue la Revolucion Francesa?",
            contexto_pdf="",
            imagen_bytes=None,
            materia="Sociales",
            historial_mensajes=[],
        )

        body = mock_post.call_args[1]["json"]
        assert "grok" in body["model"].lower()

    @patch("core.ai_engine.requests.post")
    def test_lectura_critica_usa_grok(self, mock_post):
        """Lectura Critica debe usar Grok"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Analisis lectura"}}]
        }

        llamar_profe_saber(
            mensaje_usuario="Analiza este texto",
            contexto_pdf="",
            imagen_bytes=None,
            materia="Lectura Critica",
            historial_mensajes=[],
        )

        body = mock_post.call_args[1]["json"]
        assert "grok" in body["model"].lower()

    @patch("core.ai_engine.requests.post")
    def test_otras_materias_usa_gemini(self, mock_post):
        """Otras materias deben usar Gemini"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Respuesta general"}}]
        }

        llamar_profe_saber(
            mensaje_usuario="Pregunta general",
            contexto_pdf="",
            imagen_bytes=None,
            materia="Ciencias Naturales",
            historial_mensajes=[],
        )

        body = mock_post.call_args[1]["json"]
        assert "gemini" in body["model"].lower() or "google" in body["model"].lower()


class TestPromptSocratico:
    """Tests para verificar el prompt del metodo socratico"""

    def test_profe_saber_prompt_existe(self):
        """El prompt PROFE_SABER_PROMPT debe estar definido"""
        from core.ai_engine import PROFE_SABER_PROMPT

        assert PROFE_SABER_PROMPT is not None
        assert len(PROFE_SABER_PROMPT) > 100

    def test_prompt_contiene_metodo_socratico(self):
        """El prompt debe mencionar el metodo socratico"""
        from core.ai_engine import PROFE_SABER_PROMPT

        prompt_lower = PROFE_SABER_PROMPT.lower()

        assert "socr" in prompt_lower or "pregunta" in prompt_lower
        assert "guia" in prompt_lower or "guia" in prompt_lower

    def test_prompt_menciona_no_dar_respuestas_directas(self):
        """El prompt debe instruir a no dar respuestas directas"""
        from core.ai_engine import PROFE_SABER_PROMPT

        prompt_lower = PROFE_SABER_PROMPT.lower()

        assert "no" in prompt_lower

    def test_prompt_anti_alucinacion_matematicas(self):
        """El prompt debe tener instrucciones contra alucinaciones"""
        from core.ai_engine import PROFE_SABER_PROMPT

        prompt_lower = PROFE_SABER_PROMPT.lower()

        assert "rigor" in prompt_lower or "verifica" in prompt_lower


class TestManejoHistorial:
    """Tests para el manejo del historial de conversacion"""

    @patch("core.ai_engine.requests.post")
    def test_historial_incluido_en_request(self, mock_post):
        """El historial debe incluirse en los mensajes al LLM"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Respuesta con contexto"}}]
        }

        historial = [
            {"role": "user", "content": "Primera pregunta"},
            {"role": "assistant", "content": "Primera respuesta"},
        ]

        llamar_profe_saber(
            mensaje_usuario="Segunda pregunta con contexto",
            contexto_pdf="",
            imagen_bytes=None,
            materia="Fisica",
            historial_mensajes=historial,
        )

        messages = mock_post.call_args[1]["json"]["messages"]
        assert len(messages) == 1 + len(historial) + 1
        assert messages[1]["content"] == "Primera pregunta"
        assert messages[2]["content"] == "Primera respuesta"

    @patch("core.ai_engine.requests.post")
    def test_historial_vacio_funciona(self, mock_post):
        """Debe funcionar con historial vacio"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Primera respuesta"}}]
        }

        respuesta = llamar_profe_saber(
            mensaje_usuario="Primera pregunta",
            contexto_pdf="",
            imagen_bytes=None,
            materia="Quimica",
            historial_mensajes=[],
        )

        assert respuesta


class TestManejoContextoRAG:
    """Tests para la integracion del contexto RAG"""

    @patch("core.ai_engine.requests.post")
    def test_contexto_rag_incluido(self, mock_post):
        """El contexto RAG debe incluirse en el prompt"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Respuesta con RAG"}}]
        }

        contexto_rag = "El teorema de Pitagoras establece que a^2 + b^2 = c^2"

        llamar_profe_saber(
            mensaje_usuario="Explica el teorema de Pitagoras",
            contexto_pdf=contexto_rag,
            imagen_bytes=None,
            materia="Matematicas",
            historial_mensajes=[],
        )

        messages = mock_post.call_args[1]["json"]["messages"]
        user_content = messages[-1]["content"][0]["text"]
        assert "Pitagoras" in user_content

    @patch("core.ai_engine.requests.post")
    def test_contexto_vacio_funciona(self, mock_post):
        """Debe funcionar sin contexto RAG"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Respuesta sin RAG"}}]
        }

        respuesta = llamar_profe_saber(
            mensaje_usuario="Pregunta general",
            contexto_pdf="",
            imagen_bytes=None,
            materia="Biologia",
            historial_mensajes=[],
        )

        assert respuesta


class TestManejoImagenes:
    """Tests para el procesamiento de imagenes"""

    @patch("core.ai_engine.requests.post")
    def test_imagen_codificada_correctamente(self, mock_post):
        """La imagen debe enviarse en formato base64 correcto"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Analisis de imagen"}}]
        }

        llamar_profe_saber(
            mensaje_usuario="Analiza esta imagen",
            contexto_pdf="",
            imagen_bytes=b"fake_image_content",
            materia="Matematicas",
            historial_mensajes=[],
        )

        messages = mock_post.call_args[1]["json"]["messages"]
        content = messages[-1]["content"]
        image_part = content[1]
        assert image_part["type"] == "image_url"
        assert image_part["image_url"]["url"].startswith("data:image/jpeg;base64,")


class TestManejoErrores:
    """Tests para el manejo de errores de la API"""

    @patch("core.ai_engine.requests.post")
    def test_error_api_manejado(self, mock_post):
        """Debe manejar errores de la API correctamente"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "error": {"message": "Internal Server Error"}
        }

        respuesta = llamar_profe_saber(
            mensaje_usuario="Test",
            contexto_pdf="",
            imagen_bytes=None,
            materia="Matematicas",
            historial_mensajes=[],
        )

        assert "problema" in respuesta.lower() or "error" in respuesta.lower()

    @patch("core.ai_engine.requests.post")
    def test_timeout_manejado(self, mock_post):
        """Debe manejar timeouts de la API"""
        from core.ai_engine import llamar_profe_saber
        import requests

        mock_post.side_effect = requests.Timeout("Request timed out")

        respuesta = llamar_profe_saber(
            mensaje_usuario="Test",
            contexto_pdf="",
            imagen_bytes=None,
            materia="Matematicas",
            historial_mensajes=[],
        )

        assert "conexion" in respuesta.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
