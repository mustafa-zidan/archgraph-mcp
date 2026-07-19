FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src/ src/
COPY sample_repo/ sample_repo/

RUN uv sync --locked --no-dev --no-editable

ENV PATH="/app/.venv/bin:${PATH}"
ENV REPO_PATH=/app
ENV PORT=3847
ENV MCP_TRANSPORT=streamable-http

EXPOSE 3847

CMD ["archgraph-mcp", "serve", "/app", "--transport", "streamable-http"]
