import os
from typing import List, Dict, Optional, AsyncGenerator
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class ChatManager:
    def __init__(self, model_name: str = "qwen2.5:3b", base_url: str = "http://127.0.0.1:11434"):
        self.model_name = model_name
        self.base_url = base_url
        # In-memory session storage: {session_id: [messages]}
        self.sessions: Dict[str, List] = {}
        
        self.system_prompt = (
            "Role: ANUCDE Academic Assistant. Rules: 1. Use FAQ Context ONLY. 2. No context? "
            "'Information unavailable. Contact WhatsApp.' 3. No guesses. 4. No login assumptions. "
            "5. Redirect grievances: https://wa.me/91XXXXXXXXXX. 6. Use bullets. "
            "7. Output ONLY the answer; DO NOT repeat labels like 'Proposed Answer'."
        )
        
        # Initialize LangChain ChatOllama with CPU optimization
        self.llm = ChatOllama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=0,
            num_thread=4  # Optimized for 4 CPU cores
        )

    async def get_response_stream(self, session_id: str, user_query: str, context: Optional[str] = None) -> AsyncGenerator[str, None]:
        if session_id not in self.sessions:
            self.sessions[session_id] = [SystemMessage(content=self.system_prompt)]
        
        # Prepare the message content with context if available
        content = user_query
        if context:
            content = f"FAQ Context: {context}\n\nStudent Query: {user_query}"
        
        self.sessions[session_id].append(HumanMessage(content=content))
        
        # Limit history to last 10 messages to avoid context bloat
        messages = [self.sessions[session_id][0]] + self.sessions[session_id][-10:] if len(self.sessions[session_id]) > 10 else self.sessions[session_id]

        full_response = ""
        try:
            # Note: num_thread=4 is set in __init__
            print(f"DEBUG: [PERF] Calling LLM.astream (Model: {self.model_name})")
            async for chunk in self.llm.astream(messages):
                token = chunk.content
                full_response += token
                yield token
            
            # Store the final full response in history
            self.sessions[session_id].append(AIMessage(content=full_response))
            
        except Exception as e:
            error_msg = f"\n[Error: {type(e).__name__}: {e}]"
            print(f"ERROR in streaming Ollama: {error_msg}")
            yield "I apologize, but I'm currently unable to process your request. Please ensure Ollama is running."

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
