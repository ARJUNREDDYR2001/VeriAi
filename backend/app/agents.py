"""
AI Agent Management and OpenAI Integration
Handles agent conversations and caching for cost optimization
"""

import os
import json
import time
import hashlib
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class AgentManager:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        org_id = os.getenv("OPENAI_ORG_ID")
        
        if org_id:
            self.client = OpenAI(api_key=api_key, organization=org_id)
        else:
            self.client = OpenAI(api_key=api_key)
            
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.cache_file = "chat_cache.json"
        self.cache = self._load_cache()
        self.conversations: Dict[str, List[Dict]] = {}
    
    def _load_cache(self) -> Dict:
        """Load cached responses to avoid repeated API calls"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Failed to save cache: {e}")
    
    def _get_cache_key(self, agent_id: str, message: str) -> str:
        """Generate cache key for message"""
        content = f"{agent_id}:{message}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def chat_with_agent(self, agent_id: str, message: str, conversation_id: Optional[str] = None) -> Dict:
        """Chat with AI agent using OpenAI API with caching"""
        
        # Check cache first
        cache_key = self._get_cache_key(agent_id, message)
        if cache_key in self.cache:
            cached_response = self.cache[cache_key]
            cached_response["from_cache"] = True
            return cached_response
        
        try:
            # Get conversation history
            conv_id = conversation_id or f"{agent_id}_default"
            if conv_id not in self.conversations:
                self.conversations[conv_id] = []
            
            conversation = self.conversations[conv_id]
            
            # Build messages for OpenAI
            messages = [
                {
                    "role": "system", 
                    "content": self._get_agent_system_prompt(agent_id)
                }
            ]
            
            # Add conversation history (last 5 messages to save tokens)
            for msg in conversation[-5:]:
                messages.append(msg)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=150,  # Keep responses short for cost control
                temperature=0.7
            )
            
            assistant_message = response.choices[0].message.content
            
            # Update conversation history
            conversation.append({"role": "user", "content": message})
            conversation.append({"role": "assistant", "content": assistant_message})
            
            # Keep conversation history manageable
            if len(conversation) > 20:
                conversation = conversation[-20:]
            
            self.conversations[conv_id] = conversation
            
            # Prepare response
            response_data = {
                "agent_id": agent_id,
                "content": assistant_message,
                "timestamp": time.time(),
                "tokens_used": response.usage.total_tokens,
                "from_cache": False
            }
            
            # Cache the response
            self.cache[cache_key] = response_data.copy()
            self._save_cache()
            
            return response_data
            
        except Exception as e:
            return {
                "agent_id": agent_id,
                "content": f"Error: {str(e)}",
                "timestamp": time.time(),
                "tokens_used": 0,
                "from_cache": False,
                "error": True
            }
    
    def _get_agent_system_prompt(self, agent_id: str) -> str:
        """Get system prompt for specific agent"""
        
        base_prompt = "You are an AI agent in a verification protocol demo. Keep responses short and natural."
        
        if agent_id == "agent_a":
            return f"{base_prompt} You are Agent A (Requester) - you initiate handshakes and verify other agents."
        
        elif agent_id == "agent_b":
            return f"{base_prompt} You are Agent B (Genuine Responder) - you respond to handshakes authentically."
        
        elif agent_id.startswith("fake"):
            return f"{base_prompt} You are a fake agent trying to impersonate others. Be slightly suspicious in responses."
        
        else:
            return base_prompt
    
    def get_agent_conversation(self, agent_id: str, conversation_id: Optional[str] = None) -> List[Dict]:
        """Get conversation history for agent"""
        conv_id = conversation_id or f"{agent_id}_default"
        return self.conversations.get(conv_id, [])
    
    def clear_conversation(self, agent_id: str, conversation_id: Optional[str] = None):
        """Clear conversation history"""
        conv_id = conversation_id or f"{agent_id}_default"
        if conv_id in self.conversations:
            del self.conversations[conv_id]
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "cached_responses": len(self.cache),
            "active_conversations": len(self.conversations),
            "cache_file_exists": os.path.exists(self.cache_file)
        }
    
    def estimate_cost(self, tokens_used: int) -> float:
        """Estimate cost for tokens used (gpt-4o-mini pricing)"""
        # gpt-4o-mini: ~$0.0001 per 1K tokens (approximate)
        cost_per_1k_tokens = 0.0001
        return (tokens_used / 1000) * cost_per_1k_tokens
    
    def generate_agent_response(self, agent_type: str, context: str) -> str:
        """Generate contextual response for agent type"""
        
        responses = {
            "genuine": [
                "I'm ready to verify my identity through the handshake protocol.",
                "Proceeding with cryptographic signature generation.",
                "Identity verification complete. Entering secure mode.",
                "Authenticated successfully. Ready for secure communication."
            ],
            "fake": [
                "Sure, I can verify... let me try to sign this.",
                "Processing verification... having some technical difficulties.",
                "Attempting to generate signature... please wait.",
                "Identity check in progress... almost ready."
            ]
        }
        
        import random
        return random.choice(responses.get(agent_type, responses["genuine"]))