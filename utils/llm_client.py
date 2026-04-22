"""Provider-neutral structured LLM client helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel


DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"
DEFAULT_ANTHROPIC_MAX_TOKENS = 20_000
DEFAULT_ANTHROPIC_TOOL_TIMEOUT = 240.0

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"

    @classmethod
    def parse(cls, value: str | LLMProvider | None) -> LLMProvider:
        if isinstance(value, cls):
            return value
        normalized = (value or cls.OPENAI.value).strip().lower()
        try:
            return cls(normalized)
        except ValueError as exc:
            valid = ", ".join(provider.value for provider in cls)
            raise ValueError(f"Unsupported LLM provider '{value}'. Valid choices: {valid}") from exc


@dataclass(frozen=True)
class NormalizedUsage:
    """Provider-neutral token usage fields consumed by long-run logging."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


@dataclass(frozen=True)
class ParsedLLMResponse(Generic[SchemaT]):
    """Small compatibility wrapper exposing a stable parsed response shape."""

    output_parsed: SchemaT
    raw_response: Any
    provider: str
    model: str
    usage: NormalizedUsage | None = None


def default_model_for_provider(provider: str | LLMProvider | None) -> str:
    """Return the project default model for a provider."""

    parsed = LLMProvider.parse(provider)
    if parsed is LLMProvider.ANTHROPIC:
        return DEFAULT_ANTHROPIC_MODEL
    return DEFAULT_OPENAI_MODEL


def normalize_usage(usage: Any) -> NormalizedUsage | None:
    """Convert provider-specific usage objects into common token fields."""

    if usage is None:
        return None

    def _value(*names: str) -> int | None:
        for name in names:
            if isinstance(usage, dict) and usage.get(name) is not None:
                return int(usage[name])
            if hasattr(usage, name) and getattr(usage, name) is not None:
                return int(getattr(usage, name))
        return None

    input_tokens = _value("input_tokens", "prompt_tokens")
    output_tokens = _value("output_tokens", "completion_tokens")
    total_tokens = _value("total_tokens")
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens
    if input_tokens is None and output_tokens is None and total_tokens is None:
        return None
    return NormalizedUsage(
        input_tokens=input_tokens or 0,
        output_tokens=output_tokens or 0,
        total_tokens=total_tokens or ((input_tokens or 0) + (output_tokens or 0)),
    )


def resolve_provider_from_context(run_context: Any) -> LLMProvider:
    """Resolve provider from an ExtractorRunContext-like object."""

    shared_state = getattr(run_context, "shared_state", {}) or {}
    return LLMProvider.parse(shared_state.get("llm_provider", LLMProvider.OPENAI.value))


def parse_structured(
    *,
    provider: str | LLMProvider | None = None,
    model: str,
    input: list[dict[str, Any]],
    text_format: type[SchemaT],
    timeout: float | int | None = None,
    **kwargs: Any,
) -> ParsedLLMResponse[SchemaT]:
    """Parse a structured LLM response with a provider-neutral interface."""

    parsed_provider = LLMProvider.parse(provider)
    if parsed_provider is LLMProvider.OPENAI:
        return _parse_openai(
            model=model,
            input=input,
            text_format=text_format,
            timeout=timeout,
            **kwargs,
        )
    if parsed_provider is LLMProvider.ANTHROPIC:
        return _parse_anthropic(
            model=model,
            input=input,
            text_format=text_format,
            timeout=timeout,
            **kwargs,
        )
    raise AssertionError(f"Unhandled provider: {parsed_provider}")


def _parse_openai(
    *,
    model: str,
    input: list[dict[str, Any]],
    text_format: type[SchemaT],
    timeout: float | int | None,
    **kwargs: Any,
) -> ParsedLLMResponse[SchemaT]:
    """OpenAI Responses API adapter preserving the previous call pattern."""

    from openai import OpenAI

    client = OpenAI(timeout=timeout) if timeout is not None else OpenAI()
    raw_response = client.responses.parse(
        model=model,
        input=input,
        text_format=text_format,
        **kwargs,
    )
    return ParsedLLMResponse(
        output_parsed=raw_response.output_parsed,
        raw_response=raw_response,
        provider=LLMProvider.OPENAI.value,
        model=model,
        usage=normalize_usage(getattr(raw_response, "usage", None)),
    )


def _parse_anthropic(
    *,
    model: str,
    input: list[dict[str, Any]],
    text_format: type[SchemaT],
    timeout: float | int | None,
    **kwargs: Any,
) -> ParsedLLMResponse[SchemaT]:
    """Anthropic Messages adapter with Pydantic structured output."""

    from anthropic import Anthropic

    system, messages = _convert_openai_input_to_anthropic(input)
    max_tokens = int(kwargs.pop("max_tokens", DEFAULT_ANTHROPIC_MAX_TOKENS))
    client = Anthropic()
    schema = text_format.model_json_schema()
    if _should_use_anthropic_tool_first(schema):
        raw_response, parsed = _parse_anthropic_with_tool(
            client=client,
            model=model,
            system=system,
            messages=messages,
            text_format=text_format,
            schema=schema,
            max_tokens=max_tokens,
            timeout=timeout,
            kwargs=kwargs,
        )
    else:
        try:
            raw_response = client.messages.parse(
                model=model,
                system=system,
                messages=messages,
                output_format=text_format,
                max_tokens=max_tokens,
                timeout=timeout,
                **kwargs,
            )
            parsed = getattr(raw_response, "parsed_output", None)
            if parsed is None:
                raise ValueError("Anthropic response did not include parsed_output")
        except Exception as exc:
            if not _should_use_anthropic_tool_fallback(exc):
                raise
            raw_response, parsed = _parse_anthropic_with_tool(
                client=client,
                model=model,
                system=system,
                messages=messages,
                text_format=text_format,
                schema=schema,
                max_tokens=max_tokens,
                timeout=timeout,
                kwargs=kwargs,
            )
    return ParsedLLMResponse(
        output_parsed=parsed,
        raw_response=raw_response,
        provider=LLMProvider.ANTHROPIC.value,
        model=model,
        usage=normalize_usage(getattr(raw_response, "usage", None)),
    )


def _should_use_anthropic_tool_first(schema: dict[str, Any]) -> bool:
    """Use tools directly for nested schemas that Anthropic grammar may reject."""

    return bool(schema.get("$defs"))


def _should_use_anthropic_tool_fallback(exc: Exception) -> bool:
    """Return true for Anthropic output-format failures that tools can avoid."""

    name = type(exc).__name__
    detail = str(exc).lower()
    if name == "BadRequestError" and (
        "grammar compilation timed out" in detail
        or "schema is too complex" in detail
        or "could not generate json schema" in detail
    ):
        return True
    if name == "ValueError" and "parsed_output" in detail:
        return True
    if name == "APITimeoutError" and "timed out" in detail:
        return True
    return False


def _parse_anthropic_with_tool(
    *,
    client: Any,
    model: str,
    system: str,
    messages: list[dict[str, Any]],
    text_format: type[SchemaT],
    schema: dict[str, Any],
    max_tokens: int,
    timeout: float | int | None,
    kwargs: dict[str, Any],
) -> tuple[Any, SchemaT]:
    """Fallback for Anthropic schemas too complex for output_format grammar."""

    tool_name = "emit_structured_response"
    effective_timeout = max(float(timeout or 0), DEFAULT_ANTHROPIC_TOOL_TIMEOUT)
    raw_response = client.messages.create(
        model=model,
        system=system,
        messages=messages,
        max_tokens=max_tokens,
        tools=[
            {
                "name": tool_name,
                "description": "Emit the structured response matching the provided JSON schema.",
                "input_schema": schema,
            }
        ],
        tool_choice={"type": "tool", "name": tool_name},
        timeout=effective_timeout,
        **kwargs,
    )
    for block in getattr(raw_response, "content", []) or []:
        if getattr(block, "type", "") == "tool_use" and getattr(block, "name", "") == tool_name:
            return raw_response, text_format.model_validate(getattr(block, "input", {}))
    raise ValueError("Anthropic tool fallback did not return a structured tool_use block")


def _convert_openai_input_to_anthropic(input_messages: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    """Convert OpenAI Responses-style input messages into Anthropic messages."""

    system_parts: list[str] = []
    messages: list[dict[str, Any]] = []
    for message in input_messages:
        role = str(message.get("role", "user") or "user")
        content = message.get("content", "")
        if role == "system":
            system_text = _content_to_system_text(content)
            if system_text:
                system_parts.append(system_text)
            continue
        anthropic_role = "assistant" if role == "assistant" else "user"
        messages.append({"role": anthropic_role, "content": _convert_anthropic_content(content)})
    if not messages:
        messages.append({"role": "user", "content": ""})
    return "\n\n".join(system_parts), messages


def _content_to_system_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(block.get("text", "")) for block in content if isinstance(block, dict) and block.get("text"))
    return str(content or "")


def _convert_anthropic_content(content: Any) -> str | list[dict[str, Any]]:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return str(content or "")
    converted: list[dict[str, Any]] = []
    for block in content:
        if not isinstance(block, dict):
            converted.append({"type": "text", "text": str(block)})
            continue
        block_type = block.get("type")
        if block_type in {"input_text", "text"}:
            converted.append({"type": "text", "text": str(block.get("text", ""))})
        elif block_type in {"input_image", "image"}:
            image_url = str(block.get("image_url") or block.get("url") or "")
            converted.append(_anthropic_image_block(image_url))
        else:
            converted.append({"type": "text", "text": str(block)})
    return converted


def _anthropic_image_block(image_url: str) -> dict[str, Any]:
    if image_url.startswith("data:"):
        media_type, data = _parse_data_url_image(image_url)
        return {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}}
    if image_url.startswith(("http://", "https://")):
        return {"type": "image", "source": {"type": "url", "url": image_url}}
    raise ValueError("Anthropic image input requires a data URL or HTTP(S) URL")


def _parse_data_url_image(image_url: str) -> tuple[str, str]:
    header, separator, data = image_url.partition(",")
    if not separator:
        raise ValueError("Malformed image data URL")
    media_type = header.removeprefix("data:").split(";", 1)[0].strip().lower()
    if media_type == "image/jpg":
        media_type = "image/jpeg"
    if media_type not in {"image/jpeg", "image/png", "image/gif", "image/webp"}:
        raise ValueError(f"Unsupported Anthropic image media type: {media_type}")
    return media_type, data
