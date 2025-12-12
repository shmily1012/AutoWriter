from __future__ import annotations

import asyncio
import json
import os
from typing import Iterable, Optional

from agents import Agent, ModelSettings, Runner, SQLiteSession, function_tool
from agents.mcp import (
    MCPServer,
    MCPServerStreamableHttp,
    MCPServerStreamableHttpParams,
    MCPServerStdio,
    MCPServerStdioParams,
)

from novel_system.backend.core.config import get_settings
from novel_system.backend.schemas.ai import MCPServerConfig
from novel_system.backend.services.openai_client import ROLE_SYSTEM_PROMPTS
from novel_system.backend.services.vector_store import search_related_text

settings = get_settings()


def _ensure_openai_key() -> None:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured")
    os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)


def _make_search_tool(default_top_k: int):
    @function_tool
    def search_project_context(project_id: int, query: str, top_k: int = default_top_k) -> list[dict]:
        """Search vector store for related project chunks."""
        return search_related_text(project_id=project_id, query=query, top_k=top_k)

    return search_project_context


def _build_instructions(
    role: Optional[str],
    system_prompt: Optional[str],
    persona: Optional[str],
    tone: Optional[str],
    mode: Optional[str],
) -> Optional[str]:
    parts = []
    if system_prompt:
        parts.append(system_prompt)
    base_role = ROLE_SYSTEM_PROMPTS.get(role or "default") or ROLE_SYSTEM_PROMPTS["default"]
    if not system_prompt:
        parts.append(base_role)
    if persona:
        parts.append(f"Author persona: {persona}.")
    if tone:
        parts.append(f"Tone: {tone}.")
    if mode:
        parts.append(f"Mode hint: {mode}.")
    return " ".join(parts).strip() if parts else None


def _build_agent(
    role: Optional[str],
    model: Optional[str],
    enable_vector_tool: bool,
    temperature: float,
    default_top_k: int,
    instructions: Optional[str],
    max_tokens: Optional[int],
) -> Agent[None]:
    base_instructions = instructions or (
        ROLE_SYSTEM_PROMPTS.get(role or "default") or ROLE_SYSTEM_PROMPTS["default"]
    )
    if enable_vector_tool:
        base_instructions = (
            f"{base_instructions} When helpful, call the `search_project_context` tool to recall project canon."
        )
    tools = [_make_search_tool(default_top_k)] if enable_vector_tool else []
    agent_name = (role or "writer").replace("_", " ").title() or "Assistant"
    return Agent(
        name=f"{agent_name} agent",
        instructions=base_instructions,
        model=model or settings.openai_model,
        tools=tools,
        model_settings=ModelSettings(temperature=temperature, max_tokens=max_tokens),
    )


def _load_default_mcp_servers() -> list[MCPServerConfig]:
    raw = settings.default_mcp_servers
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        return [MCPServerConfig(**item) for item in parsed]
    except Exception:
        return []


async def _connect_mcp_servers(configs: Iterable[MCPServerConfig]) -> list[MCPServer]:
    servers: list[MCPServer] = []
    for cfg in configs:
        if cfg.transport == "stdio":
            if not cfg.command:
                raise ValueError("MCP stdio server requires command")
            params = MCPServerStdioParams(command=cfg.command, cwd=cfg.working_dir)
            server: MCPServer = MCPServerStdio(params)
        elif cfg.transport == "streamable_http":
            if not cfg.url:
                raise ValueError("MCP streamable_http server requires url")
            params = MCPServerStreamableHttpParams(
                url=cfg.url,
                headers=cfg.headers or {},
                timeout_seconds=cfg.timeout_seconds,
            )
            server = MCPServerStreamableHttp(params)
        else:
            raise ValueError(f"Unsupported MCP transport: {cfg.transport}")
        await server.connect()
        servers.append(server)
    return servers


async def _run_with_mcp(
    prompt: str,
    agent_kwargs: dict,
    max_turns: int,
    session: Optional[SQLiteSession],
    mcp_server_configs: list[MCPServerConfig],
) -> str:
    instructions = agent_kwargs.get("instructions")
    servers = await _connect_mcp_servers(mcp_server_configs)
    try:
        agent = _build_agent(**{**agent_kwargs, "instructions": instructions})
        agent.mcp_servers = servers
        result = await Runner.run(
            agent,
            input=prompt,
            max_turns=max_turns,
            session=session,
        )
        return result.final_output or ""
    finally:
        for server in servers:
            await server.cleanup()


def generate_agentic_text(
    prompt: str,
    *,
    project_id: Optional[int] = None,
    role: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_turns: int = 6,
    session_id: Optional[str] = None,
    use_vector_search: bool = True,
    default_top_k: int = 5,
    context_query: Optional[str] = None,
    system_prompt: Optional[str] = None,
    persona: Optional[str] = None,
    tone: Optional[str] = None,
    mode: Optional[str] = None,
    max_tokens: Optional[int] = None,
    mcp_servers: Optional[list[MCPServerConfig]] = None,
) -> str:
    """
    Generate text using the OpenAI Agents SDK with optional vector search tool access.
    """
    _ensure_openai_key()
    instructions_text = _build_instructions(
        role=role, system_prompt=system_prompt, persona=persona, tone=tone, mode=mode
    )

    allow_vector_tool = use_vector_search and project_id is not None
    agent_kwargs = dict(
        role=role,
        model=model,
        enable_vector_tool=allow_vector_tool,
        temperature=temperature,
        default_top_k=default_top_k,
        instructions=instructions_text,
        max_tokens=max_tokens,
    )
    session = SQLiteSession(session_id) if session_id else None
    full_prompt = prompt
    if context_query:
        full_prompt = f"{prompt}\n\nContext hint: {context_query}"

    effective_mcp_servers = mcp_servers or _load_default_mcp_servers()

    if effective_mcp_servers:
        return asyncio.run(
            _run_with_mcp(
                prompt=full_prompt,
                agent_kwargs=agent_kwargs,
                max_turns=max_turns,
                session=session,
                mcp_server_configs=effective_mcp_servers,
            )
        )

    agent = _build_agent(**agent_kwargs)
    result = Runner.run_sync(agent, input=full_prompt, max_turns=max_turns, session=session)
    return result.final_output or ""


__all__ = ["generate_agentic_text"]
