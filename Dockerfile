FROM python:3.13-slim
ARG GIT_REVISION=unknown
LABEL org.opencontainers.image.revision=$GIT_REVISION
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY blog ./blog
COPY src ./src
RUN useradd --create-home --uid 10001 blog
USER blog
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD ["/app/.venv/bin/python", "-m", "blog.health"]
CMD ["/app/.venv/bin/uvicorn", "blog.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-server-header", "--no-access-log"]
