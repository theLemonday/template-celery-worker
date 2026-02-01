# ==========================================
# Stage 1: The Builder (Two-Stage Install)
# ==========================================
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv --mount=type=bind,source=uv.lock,target=uv.lock --mount=type=bind,source=pyproject.toml,target=pyproject.toml uv export --frozen --no-dev --no-emit-project \
    --format=requirements-txt > \
    requirements.txt

# 3. Install dependencies
# We install these into /app/site-packages.
# Docker will CACHE this layer as long as uv.lock doesn't change.
RUN --mount=type=cache,target=/root/.cache/uv uv pip install \
    --system \
    --target /app/site-packages \
    -r requirements.txt

# --- STATION B: Custom Finish (Frequent Changes) ---
# 4. Copy the actual source code
# This layer invalidates frequently, but that's okay because the heavy lift is done.
COPY . .

RUN uv build

# 5. Install the project itself
# --no-deps: Critical! We tell pip "Trust us, dependencies are already there."
# This prevents it from re-checking the internet or the previous layer.
# This takes the code from 'src/', packages it, and installs it to site-packages
RUN uv pip install \
    --system \
    --target \
    /app/site-packages \
    dist/*.whl

# 2. OPTIMIZATION: Compile Bytecode NOW
# Since nonroot can't write to __pycache__ at runtime, we do it here.
# This ensures fast startup.
RUN python3 -m compileall /app/site-packages

# 3. SECURITY: Ensure World-Readability
# Sometimes install tools create files only readable by owner (root).
# We ensure everyone (including nonroot) can read the libraries.
RUN chmod -R a+r /app/site-packages

# ==========================================
# Stage 2: The Runner (Distroless)
# ==========================================
FROM gcr.io/distroless/python3-debian12 AS prod

# 1. Copy the combined "site-packages" (Dependencies + Your App)
COPY --from=builder /app/site-packages /usr/lib/python3/dist-packages

USER nonroot:nonroot

# 3. Entrypoint
CMD ["-m", "celery", "-A", "celery_worker.main.app", "worker", "--loglevel=info"]
