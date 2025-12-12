from typing import Optional, Literal

from pydantic import BaseModel, Field, AnyHttpUrl


class MCPServerConfig(BaseModel):
    name: Optional[str] = Field(default=None, description="Friendly name for the MCP server")
    transport: Literal["stdio", "streamable_http"] = Field(
        ..., description="Transport type for connecting to the MCP server"
    )
    command: Optional[list[str]] = Field(
        default=None,
        description="Command to start the stdio MCP server (required when transport=stdio)",
    )
    working_dir: Optional[str] = Field(
        default=None, description="Working directory for the stdio server command"
    )
    url: Optional[AnyHttpUrl] = Field(
        default=None, description="HTTP/Streamable HTTP endpoint for the MCP server"
    )
    headers: Optional[dict[str, str]] = Field(
        default=None, description="Optional headers for HTTP-based MCP server"
    )
    timeout_seconds: Optional[int] = Field(
        default=None, description="Optional timeout for HTTP-based MCP server"
    )




class AIGenerateRequest(BaseModel):
    prompt: str = Field(..., description="User prompt content")
    mode: Optional[str] = Field(
        default=None, description="Optional mode hint (outline/expand/rewrite/etc.)"
    )
    role: Optional[str] = Field(default=None, description="Optional role key for system prompt selection")
    persona: Optional[str] = Field(default=None, description="Optional author persona or voice preference")
    tone: Optional[str] = Field(default=None, description="Optional tone guidance (e.g., darker, lighter, balanced)")
    system_prompt: Optional[str] = Field(
        default=None, description="Override system prompt; default is a writing assistant"
    )
    model: Optional[str] = Field(default=None, description="Override model")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(
        default=None, description="Optional max tokens for the response"
    )
    mcp_servers: Optional[list[MCPServerConfig]] = Field(
        default=None, description="Optional list of MCP server configs to expose to the agent"
    )


class AIGenerateResponse(BaseModel):
    generated_text: str


class AgentGenerateRequest(BaseModel):
    prompt: str = Field(..., description="User prompt content")
    project_id: Optional[int] = Field(
        default=None, description="Project id to enable vector search context"
    )
    role: Optional[str] = Field(default=None, description="Optional role key for system prompt selection")
    model: Optional[str] = Field(default=None, description="Override model")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_turns: int = Field(default=6, ge=1, le=20)
    session_id: Optional[str] = Field(
        default=None, description="Session id for conversation memory"
    )
    use_vector_search: bool = Field(
        default=True, description="Enable vector search tool when project_id is provided"
    )
    default_top_k: int = Field(default=5, ge=1, le=20)
    context_query: Optional[str] = Field(
        default=None, description="Optional hint for vector search query"
    )
    mcp_servers: Optional[list[MCPServerConfig]] = Field(
        default=None, description="Optional list of MCP server configs to expose to the agent"
    )


class AgentGenerateResponse(BaseModel):
    generated_text: str
