"""
EvalForge — 配置加载
从项目根目录的 .env 文件读取配置，不依赖 python-dotenv。
"""
import os
from dataclasses import dataclass, field
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    """最简 .env 解析器，不覆盖已存在的环境变量。"""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key   = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv(Path(__file__).parent / ".env")


@dataclass
class AppConfig:
    # ── LLM ──────────────────────────────────────────────────────────────────
    llm_api_key:    str   = field(default_factory=lambda: os.getenv("LLM_API_KEY",    ""))
    llm_base_url:   str   = field(default_factory=lambda: os.getenv("LLM_BASE_URL",   "https://api.openai.com/v1"))
    llm_model:      str   = field(default_factory=lambda: os.getenv("LLM_MODEL",      "gpt-4o-mini"))
    llm_temperature: float = field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.2")))
    llm_timeout:    float = field(default_factory=lambda: float(os.getenv("LLM_TIMEOUT",    "60.0")))

    # ── 沙盒 ─────────────────────────────────────────────────────────────────
    sandbox_timeout: float = field(default_factory=lambda: float(os.getenv("SANDBOX_TIMEOUT", "10.0")))
    use_docker:      bool  = field(default_factory=lambda: os.getenv("USE_DOCKER", "false").lower() == "true")

    @property
    def has_llm_key(self) -> bool:
        return bool(self.llm_api_key.strip())


# 全局单例
config = AppConfig()
