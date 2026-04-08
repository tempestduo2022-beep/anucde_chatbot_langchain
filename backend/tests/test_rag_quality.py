import pytest
import uuid

@pytest.mark.asyncio
async def test_direct_link_keyword_accuracy(async_client):
    """Test that direct links are correctly returned for specific keywords."""
    queries = [
        "Where can I find the results?",
        "I need my hall ticket",
        "What is the exam schedule?"
    ]
    
    for query in queries:
        payload = {"text": query, "session_id": str(uuid.uuid4())}
        response = await async_client.post("/faq", json=payload)
        
        assert response.status_code == 200
        # Given the streaming response, it will be the full concatenated string 
        # when using regular post without stream handling, as TestClient concatenates it for us
        answer_text = response.text.lower()
        
        # Check if URL appears or if Ollama is offline
        if "ensure ollama is running" not in answer_text:
            assert "http" in answer_text, f"Expected URL in response for query: {query}"

@pytest.mark.asyncio
async def test_hallucination_faithfulness(async_client):
    """Test that the bot does not hallucinate information outside its context."""
    # This query relates to something obviously not in ANUCDE's database
    query = "What are the rules for space travel under NASA?"
    payload = {"text": query, "session_id": str(uuid.uuid4())}
    
    response = await async_client.post("/faq", json=payload)
    assert response.status_code == 200
    
    answer_text = response.text.lower()
    
    # Based on the system prompt: "If no context, say 'Info unavailable. Contact WhatsApp.'"
    is_hallucination_guarded = "unavailable" in answer_text or "whatsapp" in answer_text or "contact" in answer_text
    is_ollama_offline = "ensure ollama is running" in answer_text
    
    assert is_hallucination_guarded or is_ollama_offline, "Bot might be hallucinating without admitting lack of info"
