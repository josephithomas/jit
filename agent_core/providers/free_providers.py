"""Unified Multi-Provider AI Client for Free Token Providers.

Supports seamless failover across:
1. GroqCloud (Free Tier: Llama 3.3 70B, Llama 3.1 8B, Gemma 2)
2. Google AI Studio / Gemini (Free Tier: Gemini 2.0 Flash, 1.5 Flash)
3. OpenRouter Free Tier (deepseek/deepseek-r1:free, llama-3.3-70b:free)
4. GitHub Models (Free Tier via personal access token: gpt-4o-mini, phi-3.5)
5. Hugging Face Serverless API (Free Tier)
6. Local Ollama (100% offline, zero-token cost fallback)
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import urllib.request
import urllib.error

logger = logging.getLogger("FreeAIProviders")


class FreeAIProviderRouter:
    """Manages and queries free token providers with automatic failover."""

    def __init__(self):
        self.providers = [
            {
                "name": "Groq",
                "env_key": "GROQ_API_KEY",
                "url": "https://api.groq.com/openai/v1/chat/completions",
                "default_model": "llama-3.3-70b-versatile",
                "type": "openai_compatible",
            },
            {
                "name": "OpenRouter_Free",
                "env_key": "OPENROUTER_API_KEY",
                "url": "https://openrouter.ai/api/v1/chat/completions",
                "default_model": "meta-llama/llama-3.3-70b-instruct:free",
                "type": "openai_compatible",
            },
            {
                "name": "GitHub_Models",
                "env_key": "GITHUB_TOKEN",
                "url": "https://models.inference.ai.azure.com/chat/completions",
                "default_model": "gpt-4o-mini",
                "type": "openai_compatible",
            },
            {
                "name": "Gemini_Free",
                "env_key": "GEMINI_API_KEY",
                "url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
                "default_model": "gemini-2.0-flash",
                "type": "gemini_native",
            },
            {
                "name": "Local_Ollama",
                "env_key": None,  # Requires no key, checks localhost
                "url": "http://localhost:11434/v1/chat/completions",
                "default_model": "llama3.2:latest",
                "type": "openai_compatible",
            },
        ]

    def chat_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        preferred_provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatch a prompt across available free providers with auto-fallback."""
        # Order providers with preferred one first if requested
        candidates = list(self.providers)
        if preferred_provider:
            candidates.sort(key=lambda p: 0 if p["name"].lower() == preferred_provider.lower() else 1)

        errors = []
        for provider in candidates:
            provider_name = provider["name"]
            key_name = provider["env_key"]
            api_key = os.environ.get(key_name) if key_name else ""

            # Skip if key is required but missing
            if key_name and not api_key:
                continue

            try:
                if provider["type"] == "openai_compatible":
                    result = self._query_openai_compatible(
                        url=provider["url"],
                        api_key=api_key,
                        model=provider["default_model"],
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    return {
                        "provider": provider_name,
                        "model": provider["default_model"],
                        "content": result,
                        "success": True,
                    }

                elif provider["type"] == "gemini_native":
                    result = self._query_gemini_native(
                        url_template=provider["url"],
                        api_key=api_key,
                        model=provider["default_model"],
                        messages=messages,
                        temperature=temperature,
                    )
                    return {
                        "provider": provider_name,
                        "model": provider["default_model"],
                        "content": result,
                        "success": True,
                    }

            except Exception as e:
                err_msg = f"{provider_name} failed: {str(e)}"
                logger.warning(err_msg)
                errors.append(err_msg)
                continue

        return {
            "success": False,
            "content": "",
            "errors": errors,
            "message": "All free provider candidates were either unconfigured or exhausted.",
        }

    def _query_openai_compatible(
        self,
        url: str,
        api_key: str,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        payload = json.dumps(
            {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        ).encode("utf-8")

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]

    def _query_gemini_native(
        self,
        url_template: str,
        api_key: str,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
    ) -> str:
        url = url_template.format(model=model, key=api_key)

        # Convert standard chat messages to Gemini contents structure
        contents = []
        for msg in messages:
            role = "user" if msg["role"] in ("user", "system") else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        payload = json.dumps(
            {
                "contents": contents,
                "generationConfig": {"temperature": temperature},
            }
        ).encode("utf-8")

        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidates = data.get("candidates", [])
            if candidates:
                return candidates[0]["content"]["parts"][0]["text"]
            return ""
