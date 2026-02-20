"""
Tests para el sistema RAG (Retrieval Augmented Generation).
Verifica que la busqueda en Pinecone funcione correctamente.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestBusquedaContexto:
    """Tests para la busqueda de contexto en Pinecone"""

    @patch("core.rag_search.OpenAI")
    @patch("core.rag_search.Pinecone")
    def test_busqueda_exitosa(self, mock_pinecone_cls, mock_openai_cls):
        """Debe retornar contexto relevante cuando encuentra coincidencias"""
        from core.rag_search import buscar_contexto_icfes

        mock_openai = mock_openai_cls.return_value
        mock_openai.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536)
        ]

        mock_pinecone = mock_pinecone_cls.return_value
        mock_index = mock_pinecone.Index.return_value
        mock_index.query.return_value = {
            "matches": [
                {
                    "id": "doc1",
                    "score": 0.85,
                    "metadata": {
                        "texto": "El teorema de Pitagoras establece que a^2 + b^2 = c^2",
                        "materia": "matematicas",
                    },
                },
                {
                    "id": "doc2",
                    "score": 0.78,
                    "metadata": {
                        "texto": "Los triangulos rectangulos tienen un angulo de 90 grados",
                        "materia": "matematicas",
                    },
                },
            ]
        }

        resultado = buscar_contexto_icfes("Que es el teorema de Pitagoras?", "matematicas")

        assert isinstance(resultado, str)
        assert len(resultado) > 0
        assert "Pitagoras" in resultado

    @patch("core.rag_search.OpenAI")
    @patch("core.rag_search.Pinecone")
    def test_busqueda_sin_resultados(self, mock_pinecone_cls, mock_openai_cls):
        """Debe manejar correctamente cuando no hay coincidencias"""
        from core.rag_search import buscar_contexto_icfes

        mock_openai = mock_openai_cls.return_value
        mock_openai.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536)
        ]

        mock_pinecone = mock_pinecone_cls.return_value
        mock_index = mock_pinecone.Index.return_value
        mock_index.query.return_value = {"matches": []}

        resultado = buscar_contexto_icfes("Pregunta muy especifica sin contexto", "matematicas")

        assert isinstance(resultado, str)
        assert resultado == ""

    @patch("core.rag_search.OpenAI")
    @patch("core.rag_search.Pinecone")
    def test_namespace_correcto(self, mock_pinecone_cls, mock_openai_cls):
        """Debe buscar en el namespace correcto segun la materia"""
        from core.rag_search import buscar_contexto_icfes

        mock_openai = mock_openai_cls.return_value
        mock_openai.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536)
        ]

        mock_pinecone = mock_pinecone_cls.return_value
        mock_index = mock_pinecone.Index.return_value
        mock_index.query.return_value = {"matches": []}

        materias = ["matematicas", "lectura_critica", "sociales", "ciencias_naturales", "ingles"]

        for materia in materias:
            buscar_contexto_icfes("Pregunta de prueba", materia)
            llamada = mock_index.query.call_args
            assert llamada[1]["namespace"] == materia.lower()

    @patch("core.rag_search.OpenAI")
    @patch("core.rag_search.Pinecone")
    def test_top_k_parametro(self, mock_pinecone_cls, mock_openai_cls):
        """Debe limitar el numero de resultados con top_k"""
        from core.rag_search import buscar_contexto_icfes

        mock_openai = mock_openai_cls.return_value
        mock_openai.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536)
        ]

        mock_pinecone = mock_pinecone_cls.return_value
        mock_index = mock_pinecone.Index.return_value
        mock_index.query.return_value = {"matches": []}

        buscar_contexto_icfes("Pregunta", "matematicas")

        llamada = mock_index.query.call_args
        assert llamada[1]["top_k"] == 3


class TestEmbeddings:
    """Tests para la generacion de embeddings"""

    @patch("core.rag_search.OpenAI")
    @patch("core.rag_search.Pinecone")
    def test_embedding_dimension(self, mock_pinecone_cls, mock_openai_cls):
        """Los embeddings deben tener 1536 dimensiones (text-embedding-3-small)"""
        from core.rag_search import buscar_contexto_icfes

        mock_openai = mock_openai_cls.return_value
        mock_openai.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536)
        ]

        mock_pinecone = mock_pinecone_cls.return_value
        mock_index = mock_pinecone.Index.return_value
        mock_index.query.return_value = {"matches": []}

        buscar_contexto_icfes("Test", "matematicas")

        vector_usado = mock_index.query.call_args[1]["vector"]
        assert len(vector_usado) == 1536

    @patch("core.rag_search.OpenAI")
    @patch("core.rag_search.Pinecone")
    def test_texto_vacio(self, mock_pinecone_cls, mock_openai_cls):
        """Debe manejar correctamente textos vacios"""
        from core.rag_search import buscar_contexto_icfes

        mock_openai = mock_openai_cls.return_value
        mock_openai.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536)
        ]

        mock_pinecone = mock_pinecone_cls.return_value
        mock_index = mock_pinecone.Index.return_value
        mock_index.query.return_value = {"matches": []}

        resultado = buscar_contexto_icfes("", "matematicas")
        assert isinstance(resultado, str)


class TestManejoCasosEdge:
    """Tests para casos edge y errores"""

    @patch("core.rag_search.OpenAI")
    @patch("core.rag_search.Pinecone")
    def test_error_openai(self, mock_pinecone_cls, mock_openai_cls):
        """Debe manejar errores de la API de OpenAI"""
        from core.rag_search import buscar_contexto_icfes

        mock_openai = mock_openai_cls.return_value
        mock_openai.embeddings.create.side_effect = Exception("API Error")

        with pytest.raises(Exception):
            buscar_contexto_icfes("Test", "matematicas")

    @patch("core.rag_search.OpenAI")
    @patch("core.rag_search.Pinecone")
    def test_error_pinecone(self, mock_pinecone_cls, mock_openai_cls):
        """Debe manejar errores de Pinecone"""
        from core.rag_search import buscar_contexto_icfes

        mock_openai = mock_openai_cls.return_value
        mock_openai.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536)
        ]

        mock_pinecone = mock_pinecone_cls.return_value
        mock_index = mock_pinecone.Index.return_value
        mock_index.query.side_effect = Exception("Pinecone Error")

        with pytest.raises(Exception):
            buscar_contexto_icfes("Test", "matematicas")

    @patch("core.rag_search.OpenAI")
    @patch("core.rag_search.Pinecone")
    def test_metadata_faltante(self, mock_pinecone_cls, mock_openai_cls):
        """Debe lanzar error si falta el campo texto en metadata"""
        from core.rag_search import buscar_contexto_icfes

        mock_openai = mock_openai_cls.return_value
        mock_openai.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536)
        ]

        mock_pinecone = mock_pinecone_cls.return_value
        mock_index = mock_pinecone.Index.return_value
        mock_index.query.return_value = {
            "matches": [
                {"id": "doc1", "score": 0.85, "metadata": {}}
            ]
        }

        with pytest.raises(KeyError):
            buscar_contexto_icfes("Test", "matematicas")


class TestFormateadoContexto:
    """Tests para el formateo del contexto retornado"""

    @patch("core.rag_search.OpenAI")
    @patch("core.rag_search.Pinecone")
    def test_formato_legible(self, mock_pinecone_cls, mock_openai_cls):
        """El contexto debe estar bien formateado para el LLM"""
        from core.rag_search import buscar_contexto_icfes

        mock_openai = mock_openai_cls.return_value
        mock_openai.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536)
        ]

        mock_pinecone = mock_pinecone_cls.return_value
        mock_index = mock_pinecone.Index.return_value
        mock_index.query.return_value = {
            "matches": [
                {
                    "id": "doc1",
                    "score": 0.85,
                    "metadata": {
                        "texto": "Primera fuente de informacion",
                        "materia": "matematicas",
                    },
                },
                {
                    "id": "doc2",
                    "score": 0.80,
                    "metadata": {
                        "texto": "Segunda fuente de informacion",
                        "materia": "matematicas",
                    },
                },
            ]
        }

        resultado = buscar_contexto_icfes("Test", "matematicas")

        assert isinstance(resultado, str)
        assert len(resultado) > 0
        assert "Primera fuente" in resultado or "informacion" in resultado


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
