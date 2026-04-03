"""
EvalForge — LLM Client
========================
A thin, OpenAI-compatible wrapper that works with any provider that exposes
the /chat/completions endpoint: OpenAI, DeepSeek, Moonshot, Qwen, etc.

Usage
-----
    from llm_client import LLMClient, LLMConfig, PromptBuilder

    # DeepSeek
    client = LLMClient(LLMConfig(
        api_key="sk-...",
        base_url="https://api.deepseek.com/v1",
        model="deepseek-coder",
    ))

    code = client.generate_code(
        function_signature="def add(a: int, b: int) -> int:",
        description="Return the sum of a and b.",
    )
    print(code)
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@dataclass
class LLMConfig:
    api_key: str
    model: str = "gpt-4o-mini"
    base_url: str = "https://api.openai.com/v1"
    temperature: float = 0.2        # low temp → more deterministic code
    max_tokens: int = 2048
    timeout: float = 60.0           # seconds per request
    max_retries: int = 3
    retry_delay: float = 2.0        # seconds between retries


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------


class PromptBuilder:
    """Constructs the system / user prompt pair for code-generation tasks."""

    SYSTEM_PROMPT = (
        "You are an expert Python programmer. "
        "When given a function signature and description, write ONLY the Python "
        "implementation — no explanations, no markdown fences, no extra text. "
        "The output must be valid, self-contained Python code."
    )

    @staticmethod
    def build_user_prompt(function_signature: str, description: str) -> str:
        return (
            f"Function signature:\n{function_signature}\n\n"
            f"Description:\n{description}\n\n"
            "Write the complete Python implementation:"
        )


# ---------------------------------------------------------------------------
# LLM Client
# ---------------------------------------------------------------------------


class LLMClient:
    """
    Thin wrapper around the OpenAI-compatible chat/completions API.

    Supports any provider with a compatible endpoint (OpenAI, DeepSeek, …).
    Uses httpx directly to avoid hard dependency on the openai package.

    Parameters
    ----------
    config : LLMConfig
        Connection and generation parameters.
    """

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self._http = httpx.Client(
            base_url=config.base_url,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            },
            timeout=config.timeout,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_code(self, function_signature: str, description: str) -> str:
        """
        Ask the LLM to implement *function_signature* as described.

        Returns raw Python source code (fences stripped).
        Raises LLMError on unrecoverable failures.
        """
        messages = [
            {"role": "system", "content": PromptBuilder.SYSTEM_PROMPT},
            {
                "role": "user",
                "content": PromptBuilder.build_user_prompt(function_signature, description),
            },
        ]
        raw = self._chat_with_retry(messages)
        return self._strip_fences(raw)

    def chat(self, messages: list[dict]) -> str:
        """Low-level method: send arbitrary messages, return assistant content."""
        return self._chat_with_retry(messages)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "LLMClient":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _chat_with_retry(self, messages: list[dict]) -> str:
        cfg = self.config
        last_exc: Exception | None = None

        for attempt in range(1, cfg.max_retries + 1):
            try:
                return self._call_api(messages)
            except RateLimitError as exc:
                wait = cfg.retry_delay * attempt   # exponential-ish back-off
                logger.warning("Rate limited (attempt %d/%d), retrying in %.1fs", attempt, cfg.max_retries, wait)
                time.sleep(wait)
                last_exc = exc
            except LLMError:
                raise   # non-retryable

        raise LLMError(f"All {cfg.max_retries} retries exhausted") from last_exc

    def _call_api(self, messages: list[dict]) -> str:
        cfg = self.config
        payload = {
            "model": cfg.model,
            "messages": messages,
            "temperature": cfg.temperature,
            "max_tokens": cfg.max_tokens,
        }

        try:
            response = self._http.post("/chat/completions", json=payload)
        except httpx.TimeoutException as exc:
            raise LLMError(f"Request timed out after {cfg.timeout}s") from exc
        except httpx.RequestError as exc:
            raise LLMError(f"Network error: {exc}") from exc

        if response.status_code == 429:
            raise RateLimitError("429 Too Many Requests")

        if response.status_code >= 400:
            raise LLMError(
                f"API error {response.status_code}: {response.text[:300]}"
            )

        data = response.json()
        try:
            content: str = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise LLMError(f"Unexpected response shape: {data}") from exc

        logger.debug(
            "model=%s | prompt_tokens=%s | completion_tokens=%s",
            cfg.model,
            data.get("usage", {}).get("prompt_tokens"),
            data.get("usage", {}).get("completion_tokens"),
        )
        return content

    @staticmethod
    def _strip_fences(text: str) -> str:
        """Remove markdown code fences that some models add despite instructions."""
        # Match ```python ... ``` or ``` ... ```
        match = re.search(r"```(?:python)?\n?(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class LLMError(RuntimeError):
    """Unrecoverable error from the LLM API."""


class RateLimitError(LLMError):
    """HTTP 429 — retryable."""


# ---------------------------------------------------------------------------
# Quick usage demo  (python llm_client.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    logging.basicConfig(level=logging.DEBUG)

    config = LLMConfig(
        api_key=os.environ.get("OPENAI_API_KEY", "YOUR_KEY_HERE"),
        base_url=os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"),
        model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
    )

    with LLMClient(config) as client:
        code = client.generate_code(
            function_signature="def two_sum(nums: list[int], target: int) -> list[int]:",
            description=(
                "Given an array of integers and a target, return indices of the two "
                "numbers that add up to target. Assume exactly one solution exists."
            ),
        )
        print("─── Generated code ───")
        print(code)
