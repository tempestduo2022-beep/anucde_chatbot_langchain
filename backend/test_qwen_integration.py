import httpx
import asyncio
import json

async def test_faq():
    url = "http://localhost:8000/faq"
    session_id = "test_session_123"
    
    test_queries = [
        "What is the fee for MBA?",
        "Is there an entrance exam for it?"
    ]
    
    print("Testing ANUCDE Qwen Integration...")
    print("-" * 30)
    
    for query in test_queries:
        payload = {
            "text": query,
            "session_id": session_id
        }
        
        print(f"User: {query}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    print(f"Bot: {data['answer']}")
                    print(f"Score: {data['score']}")
                    if data.get('original_answer'):
                        print(f"Context Found: Yes")
                else:
                    print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Connection Error: {e}")
        print("-" * 30)

if __name__ == "__main__":
    try:
        asyncio.run(test_faq())
    except KeyboardInterrupt:
        pass
