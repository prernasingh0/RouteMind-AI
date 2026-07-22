from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import TypeVar
from pydantic import BaseModel
from app.config.settings import get_settings

T = TypeVar("T", bound=BaseModel)

class LLMProvider(ABC):
    @abstractmethod
    async def generate_structured(self, prompt: str, output_schema: type[T]) -> T: ...
    @abstractmethod
    async def stream_text(self, prompt: str) -> AsyncIterator[str]: ...

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str | None = None) -> None:
        from openai import AsyncOpenAI
        self.settings = get_settings(); self.client = AsyncOpenAI(api_key=getattr(self.settings, "OPENAI_API_KEY", None)); self.model = model or getattr(self.settings, "OPENAI_MODEL", "gpt-4.1-mini")
    async def generate_structured(self, prompt: str, output_schema: type[T]) -> T:
        completion = await self.client.beta.chat.completions.parse(model=self.model, messages=[{"role":"user","content":prompt}], response_format=output_schema)
        parsed = completion.choices[0].message.parsed
        if parsed is None: raise ValueError("Provider returned no structured output")
        return parsed
    async def stream_text(self, prompt: str):
        stream = await self.client.chat.completions.create(model=self.model, messages=[{"role":"user","content":prompt}], stream=True)
        async for chunk in stream:
            token = chunk.choices[0].delta.content
            if token: yield token

class AzureOpenAIProvider(OpenAIProvider):
    def __init__(self, model: str | None = None) -> None:
        from openai import AsyncAzureOpenAI
        self.settings = get_settings(); self.client = AsyncAzureOpenAI(api_key=getattr(self.settings, "AZURE_OPENAI_API_KEY", None), azure_endpoint=getattr(self.settings, "AZURE_OPENAI_ENDPOINT", None), api_version=getattr(self.settings, "AZURE_OPENAI_API_VERSION", "2024-10-21")); self.model = model or getattr(self.settings, "AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini")

class LLMProviderFactory:
    @staticmethod
    def create(provider_name: str | None = None) -> LLMProvider:
        selected = (provider_name or getattr(get_settings(), "LLM_PROVIDER", "openai")).lower()
        if selected == "openai": return OpenAIProvider()
        if selected == "azure_openai": return AzureOpenAIProvider()
        raise ValueError(f"Unsupported LLM provider: {selected}")
