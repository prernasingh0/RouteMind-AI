from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import TypeVar
import os
from pydantic import BaseModel
from app.config.settings import get_settings

T = TypeVar("T", bound=BaseModel)

class LLMConfigurationError(RuntimeError):
    pass

class LLMProvider(ABC):
    @abstractmethod
    async def generate_structured(self, prompt: str, output_schema: type[T]) -> T: ...
    @abstractmethod
    async def stream_text(self, prompt: str) -> AsyncIterator[str]: ...

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str | None = None) -> None:
        from openai import AsyncOpenAI
        self.settings = get_settings()
        api_key = self.settings.OPENAI_API_KEY
        if not api_key or api_key.lower() in {"your-api-key", "change-me"}:
            raise LLMConfigurationError("OPENAI_API_KEY is not configured")
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model or self.settings.OPENAI_MODEL
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

class GeminiProvider(LLMProvider):
    def __init__(self, model: str | None = None) -> None:
        self.settings = get_settings()
        api_key = os.getenv("GEMINI_API_KEY") or self.settings.GEMINI_API_KEY
        if not api_key or api_key.lower() in {"your-api-key", "change-me"}:
            raise LLMConfigurationError("GEMINI_API_KEY is not configured")
        self.model = model or self.settings.GEMINI_MODEL
        self.api_key = api_key
        self.client = None

    def _client(self):
        if self.client is None:
            try:
                from google import genai
            except ModuleNotFoundError as exc:
                raise LLMConfigurationError("Install google-genai to use Gemini") from exc
            self.client = genai.Client(api_key=self.api_key)
        return self.client

    async def generate_structured(self, prompt: str, output_schema: type[T]) -> T:
        from pydantic import TypeAdapter
        response = await self._client().aio.models.generate_content(model=self.model, contents=prompt)
        text = getattr(response, "text", None) or "{}"
        parsed = TypeAdapter(output_schema).validate_json(text)
        return parsed

    async def stream_text(self, prompt: str):
        response = await self._client().aio.models.generate_content_stream(model=self.model, contents=prompt)
        async for chunk in response:
            text = getattr(chunk, "text", None)
            if text:
                yield text

class AzureOpenAIProvider(OpenAIProvider):
    def __init__(self, model: str | None = None) -> None:
        from openai import AsyncAzureOpenAI
        self.settings = get_settings()
        if not self.settings.AZURE_OPENAI_API_KEY or not self.settings.AZURE_OPENAI_ENDPOINT:
            raise LLMConfigurationError(
                "AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT are required"
            )
        self.client = AsyncAzureOpenAI(api_key=self.settings.AZURE_OPENAI_API_KEY, azure_endpoint=self.settings.AZURE_OPENAI_ENDPOINT, api_version=self.settings.AZURE_OPENAI_API_VERSION)
        self.model = model or self.settings.AZURE_OPENAI_DEPLOYMENT
        if not self.model:
            raise LLMConfigurationError("AZURE_OPENAI_DEPLOYMENT is required")

class LLMProviderFactory:
    @staticmethod
    def create(provider_name: str | None = None) -> LLMProvider:
        selected = (provider_name or getattr(get_settings(), "LLM_PROVIDER", "openai")).lower()
        if selected == "openai": return OpenAIProvider()
        if selected == "azure_openai": return AzureOpenAIProvider()
        if selected in {"gemini", "google_gemini"}: return GeminiProvider()
        raise ValueError(f"Unsupported LLM provider: {selected}")
