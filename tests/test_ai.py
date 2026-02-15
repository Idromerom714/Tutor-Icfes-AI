import pytest
from unittest.mock import patch, MagicMock
from core.ai_engine import llamar_profe_saber
from core.rag_search import buscar_contexto_icfes

# TEST 1: Verificar que la IA responde
@patch('requests.post')
def test_llamada_ai_exitosa(mock_post):
    # Simulamos una respuesta de OpenRouter/Kimi
    mock_post.return_value.json.return_value = {
        'choices': [{'message': {'content': '¡Hola! Soy el Profe Saber.'}}]
    }
    
    respuesta = llamar_profe_saber("Hola", "Contexto de prueba")
    assert "Profe Saber" in respuesta
    assert mock_post.called

# TEST 2: Verificar que la búsqueda en Pinecone devuelve texto
@patch('pinecone.Index')
@patch('openai.resources.embeddings.Embeddings.create')
def test_busqueda_rag(mock_embedding, mock_index):
    # Simulamos el embedding de OpenAI
    mock_embedding.return_value.data = [MagicMock(embedding=[0.1, 0.2])]
    
    # Simulamos el resultado de Pinecone
    mock_index.return_value.query.return_value = {
        'matches': [{'metadata': {'texto': 'La célula es la unidad básica.'}}]
    }
    
    contexto = buscar_contexto_icfes("¿Qué es la célula?")
    assert "unidad básica" in contexto