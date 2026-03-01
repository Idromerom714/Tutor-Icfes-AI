"""
Tests para el sistema RAG (core/rag_search.py).
"""

import pytest
from unittest.mock import patch, MagicMock


class TestBuscarContextoIcfes:
    """Tests para buscar_contexto_icfes"""

    @patch("core.rag_search.OpenAI")
    @patch("core.rag_search.Pinecone")
    def test_busqueda_con_resultados(self, mock_pinecone_cls, mock_openai_cls):
        """Debe retornar contexto cuando encuentra coincidencias"""
        from core.rag_search import buscar_contexto_icfes

        # Mock OpenAI embeddings
        mock_openai = mock_openai_cls.return_value
        mock_openai.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536)
        ]

        # Mock Pinecone query
        mock_pinecone = mock_pinecone_cls.return_value
        mock_index = mock_pinecone.Index.return_value
        mock_index.query.return_value = {
            "matches": [
                {
                    "id": "doc1",
                    "score": 0.92,
                    "metadata": {
                        "texto": "El teorema de Pitágoras establece que a² + b² = c²",
                        "materia": "matematicas"
                    }
                },
                {
                    "id": "doc2",
                    "score": 0.85,
                    "metadata": {
                        "texto": "En un triángulo rectángulo, el cuadrado de la hipotenusa...",
                        "materia": "matematicas"
                    }
                }
            ]
        }

        resultado = buscar_contexto_icfes("¿Qué es el teorema de Pitágoras?", "Matemáticas")

        assert isinstance(resultado, str)
        assert len(resultado) > 0
        assert "Pitágoras" in resultado
        assert "a² + b² = c²" in resultado

    @patch("core.rag_search.OpenAI")
    @patch("core.rag_search.Pinecone")
    def test_busqueda_sin_resultados(self, mock_pinecone_cls, mock_openai_cls):
        """Debe retornar string vacío cuando no hay coincidencias"""
        from core.rag_search import buscar_contexto_icfes

        mock_openai = mock_openai_cls.return_value
        mock_openai.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536)
        ]

        mock_pinecone = mock_pinecone_cls.return_value
        mock_index = mock_pinecone.Index.return_value
        mock_index.query.return_value = {"matches": []}

        resultado = buscar_contexto_icfes("Pregunta muy específica", "Matemáticas")

        assert isinstance(resultado, str)
        assert resultado == ""

    @patch("core.rag_search.OpenAI")
    @patch("core.rag_search.Pinecone")
    def test_namespace_correcto_por_materia(self, mock_pinecone_cls, mock_openai_cls):
        """Debe usar el namespace correcto según la materia"""
        from core.rag_search import buscar_contexto_icfes

        mock_openai = mock_openai_cls.return_value
        mock_openai.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536)
        ]

        mock_pinecone = mock_pinecone_cls.return_value
        mock_index = mock_pinecone.Index.return_value
        mock_index.query.return_value = {"matches": []}

        # Probar diferentes materias
        materias = ["Matemáticas", "Lectura Crítica", "Sociales", "Ciencias Naturales", "Inglés"]

        for materia in materias:
            buscar_contexto_icfes("Pregunta de prueba", materia)
            
            # Verificar que se llamó con namespace en minúsculas
            llamada = mock_index.query.call_args
            namespace_usado = llamada[1]["namespace"]
            assert namespace_usado == materia.lower()

    @patch("core.rag_search.OpenAI")
    @patch("core.rag_search.Pinecone")
    def test_top_k_tres_resultados(self, mock_pinecone_cls, mock_openai_cls):
        """Debe solicitar top 3 resultados"""
        from core.rag_search import buscar_contexto_icfes

        mock_openai = mock_openai_cls.return_value
        mock_openai.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536)
        ]

        mock_pinecone = mock_pinecone_cls.return_value
        mock_index = mock_pinecone.Index.return_value
        mock_index.query.return_value = {"matches": []}

        buscar_contexto_icfes("Test", "Física")

        llamada = mock_index.query.call_args
        assert llamada[1]["top_k"] == 3

    @patch("core.rag_search.OpenAI")
    @patch("core.rag_search.Pinecone")
    def test_embedding_dimension_1536(self, mock_pinecone_cls, mock_openai_cls):
        """El embedding debe tener 1536 dimensiones (text-embedding-3-small)"""
        from core.rag_search import buscar_contexto_icfes

        mock_openai = mock_openai_cls.return_value
        mock_openai.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536)
        ]

        mock_pinecone = mock_pinecone_cls.return_value
        mock_index = mock_pinecone.Index.return_value
        mock_index.query.return_value = {"matches": []}

        buscar_contexto_icfes("Test", "Matemáticas")

        # Verificar que el vector tiene 1536 dimensiones
        llamada = mock_index.query.call_args
        vector = llamada[1]["vector"]
        assert len(vector) == 1536

    @patch("core.rag_search.OpenAI")
    @patch("core.rag_search.Pinecone")
    def test_concatena_textos_con_saltos(self, mock_pinecone_cls, mock_openai_cls):
        """El contexto debe concatenar textos con doble salto de línea"""
        from core.rag_search import buscar_contexto_icfes

        mock_openai = mock_openai_cls.return_value
        mock_openai.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536)
        ]

        mock_pinecone = mock_pinecone_cls.return_value
        mock_index = mock_pinecone.Index.return_value
        mock_index.query.return_value = {
            "matches": [
                {"metadata": {"texto": "Primer chunk"}},
                {"metadata": {"texto": "Segundo chunk"}},
                {"metadata": {"texto": "Tercer chunk"}}
            ]
        }

        resultado = buscar_contexto_icfes("Test", "Matemáticas")

        assert "Primer chunk\n\nSegundo chunk\n\nTercer chunk" == resultado


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
